# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.naming import make_autoname
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, cint, add_months, date_diff
import calendar, datetime

class AnnualLeaveAllocation(Document):

	def autoname(self):
		self.name = make_autoname(self.from_date + '/.####')

	def on_submit(self):
		f_date = getdate(self.from_date)
		if not self.to_date:
			self.to_date = datetime.date(getdate(self.from_date).year, 12, 31) # month end date
		#t_date = frappe.db.sql("""select date(concat(year(%s), '-12-31'))""", (self.from_date))[0]
		if not self.employee:
			employees = frappe.db.sql("""select name, date_of_joining, date_of_birth, previous_insurance_months, employee_name 
								from `tabEmployee` where status='Active'""", as_dict=1)
		else:
			employees = frappe.db.sql("""select name, date_of_joining, date_of_birth, previous_insurance_months, employee_name 
								from `tabEmployee` where name=%s""", (self.employee), as_dict=1)
		if not employees:
			frappe.throw(_("No employee found"))
		
		leave_types = frappe.db.sql("""select * from `tabLeave Type` where default_balance>0 
							and occurrence_period=12 
							and starts_from='First of January'""", as_dict=1)
		for lv in leave_types:
			for e in employees:
				if not e.date_of_joining:
					frappe.throw(_("Date of Joining not defined for Employee {0}").format(e.employee_name))
				start_date = self.from_date
				months = get_months(getdate(e.date_of_joining), f_date) - 1
				age = flt(flt(get_months(getdate(e.date_of_birth), f_date)) / 12)
				if months <= 0:
					start_date = e.date_of_joining
					days_per = flt(flt(date_diff(self.to_date, start_date) + 1) / 365)
					new_leaves_allocated = round(flt(lv.default_balance) * days_per)
				else:
					new_leaves_allocated = flt(lv.default_balance)

				tot_months = e.previous_insurance_months + (months if months > 0 else 0)
				allocate_leave = 0
				if lv.depends_on_age == 1:
					if age >= 50:
						allocate_leave = 1
					else:
						if tot_months >= 120:
							allocate_leave = 1
				else:
					if getdate(e.date_of_joining) <= f_date:
						if lv.max_employment_age == 0:
							max_employment_age = 99999
						else:
							max_employment_age = lv.max_employment_age
						if (lv.employment_age <= months < max_employment_age) and age < 50 and tot_months < 120:
							allocate_leave = 1
				if allocate_leave == 1:
					try:
						la = frappe.new_doc('Leave Allocation')
						la.employee = e.name
						la.employee_name = e.employee_name
						la.leave_type = lv.name
						la.from_date = start_date
						la.to_date = self.to_date
						la.carry_forward = cint(lv.is_carry_forward)
						la.new_leaves_allocated = new_leaves_allocated
						la.annual_leave_allocation = self.name
						la.insert()
						la.submit()
						frappe.db.commit()
					except:
						pass

		if not self.employee:
			leave_types = frappe.db.sql("""select la.to_date, date_add(la.to_date, INTERVAL 1 day) as start_date, 
									date_add(la.to_date, INTERVAL lt.occurrence_period month) as end_date,
									la.employee, la.employee_name, la.leave_type, lt.occurrence_period, lt.leave_type, 
									lt.default_balance, lt.is_carry_forward
									from `tabLeave Allocation` la
									left join `tabLeave Type` lt on la.leave_type=lt.name
									where la.docstatus=1 and lt.leave_type='Sick Leave' and la.to_date<%s""", (self.from_date), as_dict=1)
			for lv in leave_types:
				try:
					la = frappe.new_doc('Leave Allocation')
					la.employee = lv.employee
					la.employee_name = lv.employee_name
					la.leave_type = lv.name
					la.from_date = lv.start_date
					la.to_date = lv.end_date
					#la.carry_forward = cint(lv.is_carry_forward)
					la.new_leaves_allocated = flt(lv.default_balance)
					la.annual_leave_allocation = self.name
					la.insert()
					la.submit()
					frappe.db.commit()
				except:
					pass

		excuted = frappe.db.sql("""select la.employee
								from `tabLeave Allocation` la
								left join `tabLeave Type` lt on la.leave_type=lt.name
								where la.docstatus=1 and lt.leave_type='Sick Leave' and la.to_date<%s""", (self.from_date))
		
		leave_types = frappe.db.sql("""select name, is_carry_forward, default_balance, occurrence_period 
							from `tabLeave Type` where leave_type='Sick Leave'""", as_dict=1)
							

		for e in employees:
			for lv in leave_types:
				if not e.date_of_joining:
					frappe.throw(_("Date of Joining not defined for Employee {0}").format(e.employee_name))
				end_date = add_months(e.date_of_joining, lv.occurrence_period)
				if not e.name in excuted:
					try:
						la = frappe.new_doc('Leave Allocation')
						la.employee = e.name
						la.employee_name = e.employee_name
						la.leave_type = lv.name
						la.from_date = self.from_date
						la.to_date = end_date
						#la.carry_forward = cint(lv.is_carry_forward)
						la.new_leaves_allocated = flt(lv.default_balance)
						la.annual_leave_allocation = self.name
						la.insert()
						la.submit()
						frappe.db.commit()
					except:
						pass
		
		frappe.msgprint(_("Leaves Allocated Successfully."))

	def on_cancel(self):
		leaves = frappe.db.sql("""select name from `tabLeave Allocation` where annual_leave_allocation=%s""", (self.name), as_dict=1)
		for lv in leaves:
			try:
				la = frappe.get_doc("Leave Allocation", lv.name)
				la.cancel()
				la.delete()
				frappe.db.commit()
			except:
				pass
		
		frappe.msgprint(_("Leave Allocations Successfully Deleted."))

@frappe.whitelist()
def get_months(start_date, end_date):
	diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
	return diff + 1		
