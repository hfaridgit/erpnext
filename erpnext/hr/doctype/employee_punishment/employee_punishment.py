# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import math
from frappe.utils import cint, cstr, flt, get_link_to_form, getdate
from frappe.desk.reportview import get_match_cond, get_filters_cond
from erpnext.hr.utils import set_employee_name

from frappe.model.document import Document

class EmployeePunishment(Document):

	def validate(self):
		from erpnext.setup.doctype.business_unit.business_unit import validate_bu
		validate_bu(self)
		set_employee_name(self)

		self.validate_count_before()
		
	#def on_submit(self):

		# notify leave applier about approval
		#self.notify_employee()
		#self.notify_manager()

	#def on_cancel(self):
		# notify leave applier about cancellation
		#self.notify_employee("cancelled")

	def validate_count_before(self):
		rule = frappe.get_doc("Punishment Rule", self.punishment_name)
		mtr = rule.months_to_reset_counter
		posting_month = getdate(self.posting_date).month
		if mtr > 0:
			counter = frappe.db.sql("""select count(*) as counter, start, end, m from (
								select if((month(posting_date)/%(mtr)s)-(floor(month(posting_date)/%(mtr)s))>0,
								(floor(month(posting_date)/%(mtr)s))*%(mtr)s+if((month(posting_date)/%(mtr)s)-(floor(month(posting_date)/%(mtr)s))>0,1,0), 
								((cast(month(posting_date)/%(mtr)s as INT)-1)*%(mtr)s)+1) as start, month(posting_date) as m, 
								if((month(posting_date)/%(mtr)s)-(floor(month(posting_date)/%(mtr)s))>0,
								(floor(month(posting_date)/%(mtr)s)+1)*%(mtr)s, 
								(floor(month(posting_date)/%(mtr)s))*%(mtr)s) as end 
								from `tabEmployee Punishment` 
								where docstatus=1 and employee=%(employee)s and punishment_name=%(punishment_name)s) a
								where %(posting_month)s>=start and %(posting_month)s<=end
								""", {'mtr': mtr, 'posting_month': posting_month, 'employee': self.employee, 'punishment_name': self.punishment_name}, as_dict=1)
		else:
			counter = frappe.db.sql("""select count(*) as counter
								from `tabEmployee Punishment` 
								where docstatus=1 and employee=%(employee)s and punishment_name=%(punishment_name)s
								""", {'employee': self.employee, 'punishment_name': punishment_name}, as_dict=1)
		
		if counter:
			cntx = counter[0].counter + 1
		else:
			cntx = 1

		self.counter = cntx
		det_len = len(rule.details)
		for r in rule.details:
			if cntx > det_len:
				if r.idx == det_len:
					self.rate = r.rate
					self.punishment_type = r.punishment_type
					self.action = r.action
			else:
				if r.idx == cntx:
					self.rate = r.rate
					self.punishment_type = r.punishment_type
					self.action = r.action
			
	
	def notify_employee(self):
		employee = frappe.get_doc("Employee", self.employee)
		if not employee.user_id:
			return

		def _get_message(url=False):
			if url:
				name = get_link_to_form(self.doctype, self.name)
			else:
				name = self.name

			message = "Employee Punishment: {name}".format(name=name)+"<br>"
			message += "Date: {posting_date}".format(posting_date=self.posting_date)+"<br>"
			message += "Punishment: {punishment_name}".format(punishment_name=self.punishment_name)
			return message

		self.notify({
			# for post in messages
			"message": _get_message(url=True),
			"message_to": employee.user_id,
			"subject": (_("Punishment") + ": %s") % (self.name)
		})

	def notify_manager(self):
		employee = frappe.get_doc("Employee", self.employee)
		manager = self.get_manager()
		if manager:
			def _get_message(url=False):
				name = self.name
				employee_name = cstr(employee.employee_name)
				if url:
					name = get_link_to_form(self.doctype, self.name)
					employee_name = get_link_to_form("Employee", self.employee, label=employee_name)
				message = (_("Employee Punishment") + ": %s") % (name)+"<br>"
				message += (_("Punishment") + ": %s") % (self.punishment_name)+"<br>"
				message += (_("Employee") + ": %s") % (employee_name)+"<br>"
				message += (_("Date") + ": %s") % (self.posting_date)
				return message

			self.notify({
				# for post in messages
				"message": _get_message(url=True),
				"message_to": manager,

				# for email
				"subject": (_("New Punishment") + ": %s - " + _("Employee") + ": %s") % (self.name, cstr(employee.employee_name))
			})

	def notify(self, args):
		args = frappe._dict(args)
		from frappe.desk.page.chat.chat import post
		post(**{"txt": args.message, "contact": args.message_to, "subject": args.subject,
			"notify": 1})

	def get_manager(self):
		if not self.employee:
			frappe.throw(_("Please select Employee Record first."))

		employee_manager = frappe.get_value("Employee", self.employee, "reports_to")
		manager_user = frappe.get_value("Employee", employee_manager, "user_id")

		return manager_user

