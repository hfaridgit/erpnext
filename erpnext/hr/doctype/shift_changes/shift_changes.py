# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate, add_days, getdate, today
from frappe.model.document import Document

class ShiftChanges(Document):
	def validate(self):
		from erpnext.setup.doctype.business_unit.business_unit import validate_bu
		validate_bu(self)
		if getdate(self.posting_date) > getdate(today()):
			frappe.throw(_("Future Dates are not acceptable. You can only define shifts for dates before Today."))
			
	def on_submit(self):
		sh = frappe.db.sql("""select shift from `tabShift Changes` where employee=%(emp)s 
				and posting_date=(select max(posting_date) from`tabShift Changes` where employee=%(emp)s and docstatus=1) 
				order by modified desc limit 1 """, {"emp": self.employee}, as_dict=1)
		if sh:
			frappe.db.set_value("Employee", self.employee, "shift", sh[0].shift)
			#emp = frappe.get_doc("Employee", self.employee)
			#emp.shift = sh[0].shift
			#emp.save()

	def on_cancel(self):
		frappe.msgprint(_("Please Update the Shift in Employee Form."))
		