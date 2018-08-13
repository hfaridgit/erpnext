# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import math
from frappe.utils import cint, cstr, date_diff, add_days, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname
from frappe.desk.reportview import get_match_cond, get_filters_cond
from erpnext.hr.utils import set_employee_name
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.hr.doctype.employee_leave_approver.employee_leave_approver import get_approver_listx


class InvalidLeaveApproverError(frappe.ValidationError): pass
class LeaveApproverIdentityError(frappe.ValidationError): pass
class AttendanceAlreadyMarkedError(frappe.ValidationError): pass

from frappe.model.document import Document
class PermitApplication(Document):
	def get_feed(self):
		return _("{0}: From {0} of type {1}").format(self.status, self.employee_name)

	def validate(self):
		from erpnext.setup.doctype.business_unit.business_unit import validate_bu
		validate_bu(self)
		if not getattr(self, "__islocal", None) and frappe.db.exists(self.doctype, self.name):
			self.previous_doc = frappe.get_value(self.doctype, self.name, "leave_approver", as_dict=True)
		else:
			self.previous_doc = None

		set_employee_name(self)

		self.validate_balance_permits()
		self.validate_permit_overlap()
		self.validate_max_units()
		self.validate_leave_approver()
		#self.validate_attendance()
		
	def on_update(self):
		if (not self.previous_doc and self.leave_approver) or (self.previous_doc and \
				self.status == "Open" and self.previous_doc.leave_approver != self.leave_approver):
			# notify leave approver about creation
			self.notify_leave_approver()

	def on_submit(self):
		if self.status == "Open":
			frappe.throw(_("Only Permit Applications with status 'Approved' and 'Rejected' can be submitted"))

		# notify leave applier about approval
		self.notify_employee(self.status)

	def on_cancel(self):
		# notify leave applier about cancellation
		self.notify_employee("cancelled")


	def set_permit_balance_on(self):
		max_units_per_month = frappe.db.get_single_value('Permit Settings', 'max_units_per_month')
		permit_units = frappe.db.sql("""
			select sum(total_units) as total_units
			from `tabPermit Application`
			where employee=%(employee)s 
				and status="Approved" and docstatus=1
				and month(permit_date)=month(%(date)s)
		""", {
			"date": self.permit_date,
			"employee": self.employee
		}, as_dict=1)

		if not permit_units:
			pu = 0
		else:
			pu = flt(permit_units[0].total_units)
			
		if max_units_per_month:
			balance_now = flt(max_units_per_month) - pu
		else:
			balance_now = pu

		return balance_now

	def validate_balance_permits(self):
		self.permit_balance = self.set_permit_balance_on()
		if self.permit_date and self.total_units and self.employee:

			if get_holidays(self.employee, self.permit_date):
				frappe.throw(_("The date on which you are applying for permit is holiday."))

			if self.status != "Rejected" and self.permit_balance < flt(self.total_units):
				frappe.throw(_("There is not enough permit balance for this month"))

	def validate_permit_overlap(self):
		if not self.name:
			# hack! if name is null, it could cause problems with !=
			self.name = "New Permit Application"

		for d in frappe.db.sql("""
			select
				name, posting_date, permit_date, total_units
			from `tabPermit Application`
			where employee = %(employee)s and docstatus < 2 and status in ("Open", "Approved")
			and permit_date = %(permit_date)s
			and name != %(name)s""", {
				"employee": self.employee,
				"permit_date": self.permit_date,
				"name": self.name
			}, as_dict = 1):

			self.throw_overlap_error(d)

	def throw_overlap_error(self, d):
		msg = _("Employee {0} has already applied for Permit in the same date.").format(self.employee)
		frappe.throw(msg)

	def validate_max_units(self):
		max_units_per_month = frappe.db.get_single_value('Permit Settings', 'max_units_per_month')
		max_units = frappe.db.get_single_value('Permit Settings', 'max_units')
		if max_units and self.total_units > cint(max_units):
			frappe.throw(_("Permit cannot be longer than {0} hours.").format(max_units))
		if max_units_per_month and self.permit_balance < self.total_units:
			frappe.throw(_("Permit cannot be longer than {0} hours per month.").format(max_units_per_month))

	def validate_leave_approver(self):
		employee = frappe.get_doc("Employee", self.employee)
		leave_approvers = [l.leave_approver for l in employee.get("leave_approvers")]

		if len(leave_approvers) and self.leave_approver not in leave_approvers:
			frappe.throw(_("Permit approver must be one of {0}")
				.format(comma_or(leave_approvers)), InvalidLeaveApproverError)

		elif self.leave_approver and not frappe.db.sql("""select name from `tabHas Role`
			where parent=%s and role='Leave Approver'""", self.leave_approver):
			frappe.throw(_("{0} ({1}) must have role 'Leave Approver'")\
				.format(get_fullname(self.leave_approver), self.leave_approver), InvalidLeaveApproverError)

		elif self.docstatus==1 and len(leave_approvers) and self.leave_approver != frappe.session.user:
			frappe.throw(_("Only the selected Permit Approver can submit this Permit Application"),
				LeaveApproverIdentityError)

	def validate_attendance(self):
		attendance = frappe.db.sql("""select name from `tabAttendance` where employee = %s and (attendance_date = %s)
					and status = "Present" and docstatus = 1""",
			(self.employee, self.permit_date))
		if attendance:
			frappe.throw(_("Attendance for employee {0} is already marked for this day").format(self.employee),
				AttendanceAlreadyMarkedError)

	def notify_employee(self, status):
		employee = frappe.get_doc("Employee", self.employee)
		if not employee.user_id:
			return

		def _get_message(url=False):
			if url:
				name = get_link_to_form(self.doctype, self.name)
			else:
				name = self.name

			message = "Permit Application: {name}".format(name=name)+"<br>"
			message += "Date: {permit_date}".format(permit_date=self.permit_date)+"<br>"
			message += "Status: {status}".format(status=_(status))
			return message

		self.notify({
			# for post in messages
			"message": _get_message(url=True),
			"message_to": employee.user_id,
			"subject": (_("Permit Application") + ": %s - %s") % (self.name, _(status))
		})

	def notify_leave_approver(self):
		employee = frappe.get_doc("Employee", self.employee)

		def _get_message(url=False):
			name = self.name
			employee_name = cstr(employee.employee_name)
			if url:
				name = get_link_to_form(self.doctype, self.name)
				employee_name = get_link_to_form("Employee", self.employee, label=employee_name)
			message = (_("Permit Application") + ": %s") % (name)+"<br>"
			message += (_("Employee") + ": %s") % (employee_name)+"<br>"
			message += (_("Date") + ": %s") % (self.permit_date)
			return message

		self.notify({
			# for post in messages
			"message": _get_message(url=True),
			"message_to": self.leave_approver,

			# for email
			"subject": (_("New Permit Application") + ": %s - " + _("Employee") + ": %s") % (self.name, cstr(employee.employee_name))
		})

	def notify(self, args):
		args = frappe._dict(args)
		from frappe.desk.page.chat.chat import post
		post(**{"txt": args.message, "contact": args.message_to, "subject": args.subject,
			"notify": cint(self.follow_via_email)})

@frappe.whitelist()
def get_approvers(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("employee"):
		frappe.throw(_("Please select Employee Record first."))

	employee_user = frappe.get_value("Employee", filters.get("employee"), "user_id")

	approvers_list = frappe.db.sql("""select user.name, user.first_name, user.last_name from
		tabUser user, `tabEmployee Leave Approver` approver where
		approver.parent = %s
		and user.name like %s
		and approver.leave_approver=user.name""", (filters.get("employee"), "%" + txt + "%"))

	if not approvers_list:
		approvers_list = get_approver_listx(employee_user)
	return approvers_list

@frappe.whitelist()
def get_permit_balance_on(employee, date):
	max_units_per_month = frappe.db.get_single_value('Permit Settings', 'max_units_per_month')
	permit_units = frappe.db.sql("""
		select sum(total_units) as total_units
		from `tabPermit Application`
		where employee=%(employee)s 
			and status="Approved" and docstatus=1
			and month(permit_date)=month(%(date)s)
	""", {
		"date": date,
		"employee": employee
	}, as_dict=1)

	if not permit_units:
		pu = 0
	else:
		pu = flt(permit_units[0].total_units)
		
	if max_units_per_month:
		balance_now = flt(max_units_per_month) - pu
	else:
		balance_now = pu

	return balance_now

def get_holidays(employee, permit_date):
	'''get holidays between two dates for the given employee'''
	holiday_lists = get_holiday_list_for_employee(employee)
	
	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
		where h1.parent = h2.name and h1.holiday_date= %s
		and h2.name in %s""", (permit_date, holiday_lists))[0][0]

	return holidays

@frappe.whitelist()
def get_events(start, end, filters=None):
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Permit Application", filters)
	data = frappe.db.sql("""select name, permit_date, employee_name, 
		status, employee, docstatus
		from `tabPermit Application` where
		permit_date between %(start)s and %(end)s
		and docstatus < 2
		and status!="Rejected" 
		{conditions}
		""".format(conditions=conditions), {
			"start": start, 
			"end": end
		}, as_dict=True, update={"allDay": 0})

	return data

def add_holidays(events, start, end, employee, company):
	applicable_holiday_lists = get_holiday_list_for_employee(employee)
	if not applicable_holiday_lists:
		return

	for holiday in frappe.db.sql("""select name, holiday_date, description
		from `tabHoliday` where parent in %s and holiday_date=%s""",
		(applicable_holiday_lists, start), as_dict=True):
			events.append({
				"doctype": "Holiday",
				"from_date": holiday.holiday_date,
				"to_date":  holiday.holiday_date,
				"title": _("Holiday") + ": " + cstr(holiday.description),
				"name": holiday.name
			})
