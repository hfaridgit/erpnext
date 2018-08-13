# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import math
import datetime
from frappe.utils import cint, cstr, date_diff, add_days, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname
from frappe.desk.reportview import get_match_cond, get_filters_cond
from erpnext.hr.utils import set_employee_name
from erpnext.hr.doctype.leave_block_list.leave_block_list import get_applicable_block_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.hr.doctype.employee_leave_approver.employee_leave_approver import get_approver_list


class LeaveDayBlockedError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass
class InvalidLeaveApproverError(frappe.ValidationError): pass
class LeaveApproverIdentityError(frappe.ValidationError): pass
class AttendanceAlreadyMarkedError(frappe.ValidationError): pass

from frappe.model.document import Document
class LeaveApplication(Document):
	def get_feed(self):
		return _("{0}: From {0} of type {1}").format(self.status, self.employee_name, self.leave_type)

	def validate(self):
		from erpnext.setup.doctype.business_unit.business_unit import validate_bu
		validate_bu(self)
		if not getattr(self, "__islocal", None) and frappe.db.exists(self.doctype, self.name):
			self.previous_doc = frappe.get_value(self.doctype, self.name, "leave_approver", as_dict=True)
		else:
			self.previous_doc = None

		set_employee_name(self)

		self.validate_dates()
		self.validate_balance_leaves()
		self.validate_leave_overlap()
		self.validate_max_days()
		self.show_block_day_warning()
		self.validate_block_days()
		self.validate_salary_processed_days()
		self.validate_leave_approver()
		self.validate_attendance()
		self.validate_leave_type()
		
	def on_update(self):
		if (not self.previous_doc and self.leave_approver) or (self.previous_doc and \
				self.status == "Open" and self.previous_doc.leave_approver != self.leave_approver):
			# notify leave approver about creation
			self.notify_leave_approver()

	def on_submit(self):
		if self.status == "Open":
			frappe.throw(_("Only Leave Applications with status 'Approved' and 'Rejected' can be submitted"))

		self.validate_back_dated_application()

		# notify leave applier about approval
		self.notify_employee(self.status)

	def on_cancel(self):
		# notify leave applier about cancellation
		self.notify_employee("cancelled")

	def validate_dates(self):
		if self.from_date and self.to_date and (getdate(self.to_date) < getdate(self.from_date)):
			frappe.throw(_("To date cannot be before from date"))

		if self.half_day and self.half_day_date \
			and (getdate(self.half_day_date) < getdate(self.from_date)
			or getdate(self.half_day_date) > getdate(self.to_date)):

				frappe.throw(_("Half Day Date should be between From Date and To Date"))

		if not is_lwp(self.leave_type):
			self.validate_dates_acorss_allocation()
			self.validate_back_dated_application()

	def validate_dates_acorss_allocation(self):
		def _get_leave_alloction_record(date):
			allocation = frappe.db.sql("""select name from `tabLeave Allocation`
				where employee=%s and leave_type=%s and docstatus=1
				and %s between from_date and to_date""", (self.employee, self.leave_type, date))

			return allocation and allocation[0][0]

		allocation_based_on_from_date = _get_leave_alloction_record(self.from_date)
		allocation_based_on_to_date = _get_leave_alloction_record(self.to_date)

		if not frappe.db.get_value("Leave Type", self.leave_type, "allow_negative"):
			if not (allocation_based_on_from_date or allocation_based_on_to_date):
				frappe.throw(_("Application period cannot be outside leave allocation period"))

			elif allocation_based_on_from_date != allocation_based_on_to_date:
				frappe.throw(_("Application period cannot be across two alocation records"))

	def validate_back_dated_application(self):
		future_allocation = frappe.db.sql("""select name, from_date from `tabLeave Allocation`
			where employee=%s and leave_type=%s and docstatus=1 and from_date > %s
			and carry_forward=1""", (self.employee, self.leave_type, self.to_date), as_dict=1)

		if future_allocation:
			frappe.throw(_("Leave cannot be applied/cancelled before {0}, as leave balance has already been carry-forwarded in the future leave allocation record {1}")
				.format(formatdate(future_allocation[0].from_date), future_allocation[0].name))

	def validate_salary_processed_days(self):
		if not frappe.db.get_value("Leave Type", self.leave_type, "is_lwp"):
			return

		last_processed_pay_slip = frappe.db.sql("""
			select start_date, end_date from `tabSalary Slip`
			where docstatus = 1 and employee = %s
			and ((%s between start_date and end_date) or (%s between start_date and end_date))
			order by modified desc limit 1
		""",(self.employee, self.to_date, self.from_date))

		if last_processed_pay_slip:
			frappe.throw(_("Salary already processed for period between {0} and {1}, Leave application period cannot be between this date range.").format(formatdate(last_processed_pay_slip[0][0]),
				formatdate(last_processed_pay_slip[0][1])))


	def show_block_day_warning(self):
		block_dates = get_applicable_block_dates(self.from_date, self.to_date,
			self.employee, self.company, all_lists=True)

		if block_dates:
			frappe.msgprint(_("Warning: Leave application contains following block dates") + ":")
			for d in block_dates:
				frappe.msgprint(formatdate(d.block_date) + ": " + d.reason)

	def validate_block_days(self):
		block_dates = get_applicable_block_dates(self.from_date, self.to_date,
			self.employee, self.company)

		if block_dates and self.status == "Approved":
			frappe.throw(_("You are not authorized to approve leaves on Block Dates"), LeaveDayBlockedError)

	def validate_balance_leaves(self):
		if self.from_date and self.to_date:
			self.total_leave_days = self.calc_number_of_leave_days()
			#self.total_leave_days = get_number_of_leave_days(self.employee, self.leave_type,
			#	self.from_date, self.to_date, self.half_day, self.half_day_date)
			
			if self.total_leave_days == 0:
				frappe.throw(_("The day(s) on which you are applying for leave are holidays. You need not apply for leave."))

			if not is_lwp(self.leave_type):
				self.leave_balance = get_leave_balance_on(self.employee, self.leave_type, self.from_date,
					consider_all_leaves_in_the_allocation_period=True)

				if self.status != "Rejected" and self.leave_balance < self.total_leave_days:
					if frappe.db.get_value("Leave Type", self.leave_type, "next_leave_type") and self.leave_balance > 0:
						self.total_leave_days = self.leave_balance
						frappe.msgprint(_("Note: Not enough balance - leave days changed - Please change To Date."))
					else:
						if frappe.db.get_value("Leave Type", self.leave_type, "allow_negative"):
								#frappe.msgprint(_("Note: There is not enough leave balance for Leave Type {0}")
								#	.format(self.leave_type))
								h = 0
						else:
							frappe.throw(_("There is not enough leave balance for Leave Type {0}")
								.format(self.leave_type))

	def validate_leave_overlap(self):
		if not self.name:
			# hack! if name is null, it could cause problems with !=
			self.name = "New Leave Application"

		for d in frappe.db.sql("""
			select
				name, leave_type, posting_date, from_date, to_date, total_leave_days, half_day_date
			from `tabLeave Application`
			where employee = %(employee)s and docstatus < 2 and status in ("Open", "Approved")
			and to_date >= %(from_date)s and from_date <= %(to_date)s
			and name != %(name)s""", {
				"employee": self.employee,
				"from_date": self.from_date,
				"to_date": self.to_date,
				"name": self.name
			}, as_dict = 1):

			if cint(self.half_day)==1 and getdate(self.half_day_date) == getdate(d.half_day_date) and (
				flt(self.total_leave_days)==0.5
				or getdate(self.from_date) == getdate(d.to_date)
				or getdate(self.to_date) == getdate(d.from_date)):

				total_leaves_on_half_day = self.get_total_leaves_on_half_day()
				if total_leaves_on_half_day >= 1:
					self.throw_overlap_error(d)
			else:
				self.throw_overlap_error(d)

	def throw_overlap_error(self, d):
		msg = _("Employee {0} has already applied for {1} between {2} and {3}").format(self.employee,
			d['leave_type'], formatdate(d['from_date']), formatdate(d['to_date'])) \
			+ """ <br><b><a href="#Form/Leave Application/{0}">{0}</a></b>""".format(d["name"])
		frappe.throw(msg, OverlapError)

	def get_total_leaves_on_half_day(self):
		leave_count_on_half_day_date = frappe.db.sql("""select count(name) from `tabLeave Application`
			where employee = %(employee)s
			and docstatus < 2
			and status in ("Open", "Approved")
			and half_day = 1
			and half_day_date = %(half_day_date)s
			and name != %(name)s""", {
				"employee": self.employee,
				"half_day_date": self.half_day_date,
				"name": self.name
			})[0][0]

		return leave_count_on_half_day_date * 0.5

	def validate_max_days(self):
		max_days = frappe.db.get_value("Leave Type", self.leave_type, "max_days_allowed")
		if max_days and self.total_leave_days > cint(max_days):
			frappe.throw(_("Leave of type {0} cannot be longer than {1}").format(self.leave_type, max_days))

	def validate_leave_approver(self):
		employee = frappe.get_doc("Employee", self.employee)
		leave_approvers = [l.leave_approver for l in employee.get("leave_approvers")]

		if len(leave_approvers) and self.leave_approver not in leave_approvers:
			frappe.throw(_("Leave approver must be one of {0}")
				.format(comma_or(leave_approvers)), InvalidLeaveApproverError)

		elif self.leave_approver and not frappe.db.sql("""select name from `tabHas Role`
			where parent=%s and role='Leave Approver'""", self.leave_approver):
			frappe.throw(_("{0} ({1}) must have role 'Leave Approver'")\
				.format(get_fullname(self.leave_approver), self.leave_approver), InvalidLeaveApproverError)

		elif self.docstatus==1 and len(leave_approvers) and self.leave_approver != frappe.session.user:
			frappe.throw(_("Only the selected Leave Approver can submit this Leave Application"),
				LeaveApproverIdentityError)

	def validate_attendance(self):
		attendance = frappe.db.sql("""select name from `tabAttendance` where employee = %s and (attendance_date between %s and %s)
					and status = "Present" and docstatus = 1""",
			(self.employee, self.from_date, self.to_date))
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

			message = "Leave Application: {name}".format(name=name)+"<br>"
			message += "Leave Type: {leave_type}".format(leave_type=self.leave_type)+"<br>"
			message += "From Date: {from_date}".format(from_date=self.from_date)+"<br>"
			message += "To Date: {to_date}".format(to_date=self.to_date)+"<br>"
			message += "Status: {status}".format(status=_(status))
			return message

		self.notify({
			# for post in messages
			"message": _get_message(url=True),
			"message_to": employee.user_id,
			"subject": (_("Leave Application") + ": %s - %s") % (self.name, _(status))
		})

	def notify_leave_approver(self):
		employee = frappe.get_doc("Employee", self.employee)

		def _get_message(url=False):
			name = self.name
			employee_name = cstr(employee.employee_name)
			if url:
				name = get_link_to_form(self.doctype, self.name)
				employee_name = get_link_to_form("Employee", self.employee, label=employee_name)
			message = (_("Leave Application") + ": %s") % (name)+"<br>"
			message += (_("Employee") + ": %s") % (employee_name)+"<br>"
			message += (_("Leave Type") + ": %s") % (self.leave_type)+"<br>"
			message += (_("From Date") + ": %s") % (self.from_date)+"<br>"
			message += (_("To Date") + ": %s") % (self.to_date)
			return message

		self.notify({
			# for post in messages
			"message": _get_message(url=True),
			"message_to": self.leave_approver,

			# for email
			"subject": (_("New Leave Application") + ": %s - " + _("Employee") + ": %s") % (self.name, cstr(employee.employee_name))
		})

	def notify(self, args):
		args = frappe._dict(args)
		from frappe.desk.page.chat.chat import post
		post(**{"txt": args.message, "contact": args.message_to, "subject": args.subject,
			"notify": cint(self.follow_via_email)})

	def validate_leave_type(self):
		if not (self.from_date and self.to_date and self.leave_type and self.employee):
			frappe.throw(_("Mandatory Fields Required to continue - Employee, Leave Type, From Date, To date."))
			return
		employee = self.employee
		leave_type = frappe.get_doc("Leave Type", self.leave_type)
		emp = frappe.get_doc("Employee", employee)
		if leave_type.leave_type != "Sick Leave" and leave_type.starts_from == "Joining Date":
			employment_days = date_diff(self.from_date, emp.date_of_joining) + 1
			if leave_type.employment_age == 0 or employment_days > leave_type.employment_age * 30:
				occ = frappe.db.sql("""select count(leave_type) as occurrences
								from `tabLeave Application`
								where docstatus=1 and status='Approved' and leave_type=%s and employee=%s""", (leave_type.name, employee), as_dict=1)
				if occ:
					if occ[0].occurrences >= leave_type.occurrence and leave_type.occurrence>0:
						frappe.throw(_("Not Permitted, No Balance available for this Employee."))
					
		if leave_type.leave_type != "Sick Leave" and leave_type.starts_from == "First of January" and leave_type.occurrence > 0:
				occ = frappe.db.sql("""select count(leave_type) as occurrences
								from `tabLeave Application`
								where docstatus=1 and status='Approved' and leave_type=%s and employee=%s
								and year(from_date)=year(%s)""", (leave_type.name, employee, self.from_date), as_dict=1)
				if occ:
					if occ[0].occurrences >= leave_type.occurrence and leave_type.occurrence>0:
						frappe.throw(_("Not Permitted, No Balance available for this Employee."))
			
		if leave_type.leave_type == "Sick Leave":
			leave_balance = self.leave_balance
			if leave_type.next_leave_type and leave_balance <=0:
				self.leave_type = leave_type.next_leave_type
			
		if leave_type.leave_type == "Normal Leave":
			leave_balance = self.leave_balance
			if leave_type.next_leave_type and leave_balance <=0:
				occ = frappe.db.sql("""select sum(total_leave_days) as tot_days
								from `tabLeave Application`
								where docstatus=1 and status='Approved' and parent_leave_type=%s and employee=%s
								and year(from_date)=year(%s)""", (leave_type.name, employee, self.from_date), as_dict=1)
				if occ:
					if occ[0].tot_days >= leave_type.max_next_leave_days:
						if leave_type.rate_after_next_max == 0:
							self.days_rate = 1
						else:
							self.days_rate = leave_type.rate_after_next_max
					else:
						self.days_rate = 1
				self.leave_type = leave_type.next_leave_type
				self.parent_leave_type = leave_type.name
		if self.days_rate > 1:
			self.total_leave_days = self.calc_number_of_leave_days()
			#self.total_leave_days = get_number_of_leave_days(self.employee, self.leave_type, 
			#		self.from_date, self.to_date, self.days_rate, self.half_day, self.half_day_date)						

	def calc_number_of_leave_days(self):
		number_of_days = 0
		if self.half_day == 1:
			if self.from_date == self.to_date:
				number_of_days = 0.5
			else:
				number_of_days = date_diff(self.to_date, self.from_date) + .5
		else:
			number_of_days = date_diff(self.to_date, self.from_date) + 1

		if not frappe.db.get_value("Leave Type", self.leave_type, "include_holiday"):
			number_of_days = flt(number_of_days) - flt(get_holidays(self.employee, self.from_date, self.to_date))
		if self.days_rate > 1:  
			number_of_days = flt(number_of_days) * flt(self.days_rate) 
			
		start_date = getdate(self.from_date)
		end_date = getdate(self.to_date)
			
		return number_of_days + (check_saturdays(start_date, end_date) if not frappe.db.get_value("Leave Type", self.leave_type, "include_holiday") else 0)

@frappe.whitelist()
def	check_saturdays(start_date, end_date):
	i = 0
	d = start_date
	if (d.strftime("%A") != "Friday" and d.strftime("%A") != "Saturday"):
		delta = datetime.timedelta(days=1)
		while d <= end_date:
			if d.strftime("%A") == "Saturday" and  d != end_date:
			   i += 1
			d += delta	
	return i

@frappe.whitelist()
def get_leave_types(doctype, txt, searchfield, start, page_len, filters):		
	leaves_list = frappe.db.sql("""select la.leave_type as name 
						from `tabLeave Allocation` la
						left join `tabLeave Type` lt on la.leave_type=lt.name
						where %(from_date)s between la.from_date and la.to_date 
						and la.employee=%(employee)s
						and la.docstatus=1 and la.total_leaves_allocated>0
						and lt.is_self_service=1 and (la.leave_type like %(txt)s)
						group by la.leave_type
						having 1=1 
						{mcond}
						order by 
							if(locate(%(_txt)s, la.leave_type), locate(%(_txt)s, la.leave_type), 99999),
							la.leave_type
						limit %(start)s, %(page_len)s""".format(**{
							'key': searchfield,
							'mcond':get_match_cond(doctype)
						}), {
							'txt': "%%%s%%" % txt,
							'_txt': txt.replace("%", ""),
							'start': start,
							'page_len': page_len,
							'employee': filters.get("employee"), 
							'from_date': filters.get("from_date")
						})

	return leaves_list
	
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
		approvers_list = get_approver_list(employee_user)
	return approvers_list

@frappe.whitelist()
def get_number_of_leave_days(employee, leave_type, from_date, to_date, days_rate = 1, half_day = 0, half_day_date = None):
	number_of_days = 0
	if half_day == 1:
		if from_date == to_date:
			number_of_days = 0.5
		else:
			number_of_days = date_diff(to_date, from_date) + .5
	else:
		number_of_days = date_diff(to_date, from_date) + 1

	if not frappe.db.get_value("Leave Type", leave_type, "include_holiday"):
		number_of_days = flt(number_of_days) - flt(get_holidays(employee, from_date, to_date))
	if days_rate > 1:  
		number_of_days = flt(number_of_days) * flt(days_rate) 
	start_date = getdate(from_date)
	end_date = getdate(to_date)
	
	return number_of_days + (check_saturdays(start_date, end_date) if not frappe.db.get_value("Leave Type", leave_type, "include_holiday") else 0)

@frappe.whitelist()
def get_leave_balance_on(employee, leave_type, date, allocation_records=None,
		consider_all_leaves_in_the_allocation_period=False):
	if allocation_records == None:
		allocation_records = get_leave_allocation_records(date, employee).get(employee, frappe._dict())

	allocation = allocation_records.get(leave_type, frappe._dict())

	if consider_all_leaves_in_the_allocation_period:
		date = allocation.to_date
	leaves_taken = get_approved_leaves_for_period(employee, leave_type, allocation.from_date, date)

	return flt(allocation.total_leaves_allocated) - flt(leaves_taken)

def get_approved_leaves_for_period(employee, leave_type, from_date, to_date):
	leave_applications = frappe.db.sql("""
		select employee, leave_type, from_date, to_date, total_leave_days
		from `tabLeave Application`
		where employee=%(employee)s and leave_type=%(leave_type)s
			and status="Approved" and docstatus=1
			and (from_date between %(from_date)s and %(to_date)s
				or to_date between %(from_date)s and %(to_date)s
				or (from_date < %(from_date)s and to_date > %(to_date)s))
	""", {
		"from_date": from_date,
		"to_date": to_date,
		"employee": employee,
		"leave_type": leave_type
	}, as_dict=1)

	leave_days = 0
	for leave_app in leave_applications:
		if leave_app.from_date >= getdate(from_date) and leave_app.to_date <= getdate(to_date):
			leave_days += leave_app.total_leave_days
		else:
			if leave_app.from_date < getdate(from_date):
				leave_app.from_date = from_date
			if leave_app.to_date > getdate(to_date):
				leave_app.to_date = to_date

			leave_days += get_number_of_leave_days(employee, leave_type,
				leave_app.from_date, leave_app.to_date)

	return leave_days

def get_leave_allocation_records(date, employee=None):
	conditions = (" and employee='%s'" % employee) if employee else ""

	leave_allocation_records = frappe.db.sql("""
		select employee, leave_type, total_leaves_allocated, from_date, to_date
		from `tabLeave Allocation`
		where %s between from_date and to_date and docstatus=1 {0}""".format(conditions), (date), as_dict=1)

	allocated_leaves = frappe._dict()
	for d in leave_allocation_records:
		allocated_leaves.setdefault(d.employee, frappe._dict()).setdefault(d.leave_type, frappe._dict({
			"from_date": d.from_date,
			"to_date": d.to_date,
			"total_leaves_allocated": d.total_leaves_allocated
		}))

	return allocated_leaves


def get_holidays(employee, from_date, to_date):
	'''get holidays between two dates for the given employee'''
	holiday_lists = get_holiday_list_for_employee(employee)
	
	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
		where h1.parent = h2.name and h1.holiday_date between %s and %s
		and h2.name in %s""", (from_date, to_date, holiday_lists))[0][0]

	return holidays

def is_lwp(leave_type):
	lwp = frappe.db.sql("select is_lwp from `tabLeave Type` where name = %s", leave_type)
	return lwp and cint(lwp[0][0]) or 0

@frappe.whitelist()
def get_events(start, end, filters=None):
	events = []

	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, ["name", "company"],
		as_dict=True)
	if employee:
		employee, company = employee.name, employee.company
	else:
		employee=''
		company=frappe.db.get_value("Global Defaults", None, "default_company")

	from frappe.desk.reportview import get_filters_cond
	conditions = get_filters_cond("Leave Application", filters, [])

	# show department leaves for employee
	if "Employee" in frappe.get_roles():
		add_department_leaves(events, start, end, employee, company)

	add_leaves(events, start, end, conditions)

	add_block_dates(events, start, end, employee, company)
	add_holidays(events, start, end, employee, company)

	return events

def add_department_leaves(events, start, end, employee, company):
	department = frappe.db.get_value("Employee", employee, "department")

	if not department:
		return

	# department leaves
	department_employees = frappe.db.sql_list("""select name from tabEmployee where department=%s
		and company=%s""", (department, company))

	match_conditions = "and employee in (\"%s\")" % '", "'.join(department_employees)
	add_leaves(events, start, end, match_conditions=match_conditions)

def add_leaves(events, start, end, match_conditions=None):
	query = """select name, from_date, to_date, employee_name, half_day,
		status, employee, docstatus
		from `tabLeave Application` where
		from_date <= %(end)s and to_date >= %(start)s <= to_date
		and docstatus < 2
		and status!="Rejected" """
	if match_conditions:
		query += match_conditions

	for d in frappe.db.sql(query, {"start":start, "end": end}, as_dict=True):
		e = {
			"name": d.name,
			"doctype": "Leave Application",
			"from_date": d.from_date,
			"to_date": d.to_date,
			"status": d.status,
			"title": cstr(d.employee_name) + \
				(d.half_day and _(" (Half Day)") or ""),
			"docstatus": d.docstatus
		}
		if e not in events:
			events.append(e)

def add_block_dates(events, start, end, employee, company):
	# block days
	from erpnext.hr.doctype.leave_block_list.leave_block_list import get_applicable_block_dates

	cnt = 0
	block_dates = get_applicable_block_dates(start, end, employee, company, all_lists=True)

	for block_date in block_dates:
		events.append({
			"doctype": "Leave Block List Date",
			"from_date": block_date.block_date,
			"to_date": block_date.block_date,
			"title": _("Leave Blocked") + ": " + block_date.reason,
			"name": "_" + str(cnt),
		})
		cnt+=1

def add_holidays(events, start, end, employee, company):
	applicable_holiday_lists = get_holiday_list_for_employee(employee, company)
	if not applicable_holiday_lists:
		return

	for holiday in frappe.db.sql("""select name, holiday_date, description
		from `tabHoliday` where parent in %s and holiday_date between %s and %s""",
		(applicable_holiday_lists, start, end), as_dict=True):
			events.append({
				"doctype": "Holiday",
				"from_date": holiday.holiday_date,
				"to_date":  holiday.holiday_date,
				"title": _("Holiday") + ": " + cstr(holiday.description),
				"name": holiday.name
			})
