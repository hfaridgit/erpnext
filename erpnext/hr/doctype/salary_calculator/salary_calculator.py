# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext

from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words

from frappe import msgprint, _
from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils.background_jobs import enqueue

class SalaryCalculator(TransactionBase):
	def validate(self):
		if not (len(self.get("earnings")) or len(self.get("deductions"))):
			# get details from salary structure
			self.get_emp_and_leave_details()

		# if self.salary_slip_based_on_timesheet or not self.net_pay:
		self.req_sal = self.requested_salary
		if not self.net:
			self.calculate_net_pay()
		else:
			while self.rounded_total < self.requested_salary:
				self.req_sal = self.req_sal + 1
				self.calculate_net_pay()
				

		#company_currency = erpnext.get_company_currency(self.company)
		company_currency = 'EGP'
		self.total_in_words = money_in_words(self.rounded_total, company_currency)

	def calculate_component_amounts(self):
		if not getattr(self, '_salary_structure_doc', None):
			self._salary_structure_doc = frappe.get_doc('Salary Structure', self.salary_structure)

		data = self.get_data_for_eval()

		for key in ('earnings', 'deductions'):
			for struct_row in self._salary_structure_doc.get(key):
				if struct_row.abbr == "B":
					struct_row.amount = self.req_sal
					self.update_component_row(struct_row, self.req_sal, key)
				amount = self.eval_condition_and_formula(struct_row, data)
				if amount and struct_row.statistical_component == 0:
					self.update_component_row(struct_row, amount, key)
		
	def update_component_row(self, struct_row, amount, key):
		component_row = None
		for d in self.get(key):
			if d.salary_component == struct_row.salary_component:
				component_row = d

		if not component_row:
			self.append(key, {
				'amount': amount,
				'default_amount': amount,
				'depends_on_lwp' : struct_row.depends_on_lwp,
				'salary_component' : struct_row.salary_component,
				'abbr' : struct_row.abbr,
				'do_not_include_in_total' : struct_row.do_not_include_in_total
			})
		else:
			component_row.amount = amount

	def eval_condition_and_formula(self, d, data):
		try:
			condition = d.condition.strip() if d.condition else None
			if condition:
				if not frappe.safe_eval(condition, None, data):
					return None
			amount = d.amount
			if d.amount_based_on_formula:
				formula = d.formula.strip() if d.formula else None
				if formula:
					amount = frappe.safe_eval(formula, None, data)
			if amount:
				data[d.abbr] = amount

			return amount

		except NameError as err:
			frappe.throw(_("Name error: {0}".format(err)))
		except SyntaxError as err:
			frappe.throw(_("Syntax error in formula or condition: {0}".format(err)))
		except Exception as e:
			frappe.throw(_("Error in formula or condition: {0}".format(e)))
			raise

	def get_data_for_eval(self):
		'''Returns data for evaluating formula'''
		data = frappe._dict()

		data.update(self.as_dict())

		# set values for components
		salary_components = frappe.get_all("Salary Component", fields=["salary_component_abbr"])
		for sc in salary_components:
			data.setdefault(sc.salary_component_abbr, 0)

		for key in ('earnings', 'deductions'):
			for d in self.get(key):
				data[d.abbr] = d.amount
				if d.abbr == "B":
					data['B'] = self.requested_salary
					d.amount = self.requested_salary

		return data


	def get_emp_and_leave_details(self):
		'''First time, load all the components from salary structure'''
		self.set("earnings", [])
		self.set("deductions", [])

		self._salary_structure_doc = frappe.get_doc('Salary Structure', self.salary_structure)
		self.pull_sal_struct()

	def pull_sal_struct(self):
		from erpnext.hr.doctype.salary_structure.salary_structure import make_salary_calculator

		make_salary_calculator(self._salary_structure_doc.name, self)

	def process_salary_structure(self):
		'''Calculate salary after salary structure details have been updated'''
		self.calculate_net_pay()

	def get_holidays_for_employee(self, start_date, end_date):
		holiday_list = get_holiday_list_for_employee(self.employee)
		holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
			where
				parent=%(holiday_list)s
				and holiday_date >= %(start_date)s
				and holiday_date <= %(end_date)s''', {
					"holiday_list": holiday_list,
					"start_date": start_date,
					"end_date": end_date
				})

		holidays = [cstr(i) for i in holidays]

		return holidays

	def calculate_lwp(self, holidays, working_days):
		lwp = 0
		holidays = "','".join(holidays)
		for d in range(working_days):
			dt = add_days(cstr(getdate(self.start_date)), d)
			leave = frappe.db.sql("""
				select t1.name, t1.half_day
				from `tabLeave Application` t1, `tabLeave Type` t2
				where t2.name = t1.leave_type
				and t2.is_lwp = 1
				and t1.docstatus = 1
				and t1.status = 'Approved'
				and t1.employee = %(employee)s
				and CASE WHEN t2.include_holiday != 1 THEN %(dt)s not in ('{0}') and %(dt)s between from_date and to_date
				WHEN t2.include_holiday THEN %(dt)s between from_date and to_date
				END
				""".format(holidays), {"employee": self.employee, "dt": dt})
			if leave:
				lwp = cint(leave[0][1]) and (lwp + 0.5) or (lwp + 1)
		return lwp

	def sum_components(self, component_type, total_field):
		for d in self.get(component_type):
			if (self.salary_structure and
				cint(d.depends_on_lwp)):
				d.amount = rounded(
					flt(d.default_amount), self.precision("amount", component_type)
				)

			elif cint(d.depends_on_lwp):
				d.amount = 0
			elif not d.amount:
				d.amount = d.default_amount
			if not d.do_not_include_in_total:
				self.set(total_field, self.get(total_field) + flt(d.amount))

	def calculate_net_pay(self):
		if self.salary_structure:
			self.calculate_component_amounts()

		disable_rounded_total = cint(frappe.db.get_value("Global Defaults", None, "disable_rounded_total"))

		self.total_deduction = 0
		self.gross_pay = 0

		self.sum_components('earnings', 'gross_pay')
		self.sum_components('deductions', 'total_deduction')

		self.net_pay = flt(self.gross_pay) - flt(self.total_deduction)
		self.rounded_total = rounded(self.net_pay,
			self.precision("net_pay") if disable_rounded_total else 0)

