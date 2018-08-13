# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class CarOdometerRegister(Document):
	def validate(self):
		check_exist = frappe.db.sql("""select name from `tabCar Odometer Register`
						where employee=%(employee)s and ((end_date>=%(start_date)s and end_date<=%(end_date)s) or 
						(start_date>=%(start_date)s and start_date<=%(end_date)s)) and docstatus=1""", 
						{"employee": self.employee, "start_date": self.start_date, "end_date": self.end_date}, as_dict=1)
		if check_exist:
			frappe.throw(_("A Reading Already Registered Within Those Dates."))
