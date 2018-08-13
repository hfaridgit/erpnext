# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class CarOdometerPost(Document):
	def post_transactions(self):
		transactions = frappe.db.sql("""select employee, sum(end_reading-start_reading) as counter from `tabCar Odometer Register`
							where docstatus=1 and ifnull(status,'')<>'Processed' and end_date<=%s 
							group by employee""", (self.posting_date), as_dict=1)
		sst = frappe.get_doc("Salary Slip Type", self.salary_slip_type)
		sst.employees = []
		if transactions:
			for d in transactions:
				sst.append('employees', {
					'employee': d.employee, 
					'counter': d.counter
				})
		sst.save()
		frappe.db.sql("""update `tabCar Odometer Register` set status='Posted'
							where docstatus=1 and ifnull(status,'')<>'Processed' and end_date<=%s""", (self.posting_date))
		frappe.msgprint(_("Transactions Posted Successfuly."))
		
