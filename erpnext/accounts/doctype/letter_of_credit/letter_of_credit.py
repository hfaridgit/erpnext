# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt, comma_and
from frappe.model.document import Document

class LetterofCredit(Document):
	def validate(self):
		from erpnext.setup.doctype.business_unit.business_unit import validate_bu
		validate_bu(self)

	def on_submit(self):
		pj = frappe.new_doc("Project")
		pj.project_name = self.name
		pj.company = self.company
		pj.business_unit = self.business_unit
		pj.project_type = "Import Operation"
		pj.insert(ignore_permissions=True)
		self.project = pj.name
		frappe.db.set_value(self.doctype, self.name, "project",	pj.name)
		frappe.msgprint(_("Project {0} Created for this Import Operation").format(pj.name))

	def make_journal_entry(self, posting_date, cost_center=None):
		if self.project:
			je_list = []
			pj = frappe.get_doc("Project", self.project)
			cost_center = cost_center or frappe.db.get_value("Company", self.company, "cost_center")
			if not pj.project_account:
				frappe.throw(_("Project Account not Defined in Project {0}").format(self.project))
			if not pj.project_closing_account:
				frappe.throw(_("Project Closing Account not Defined in Project {0}").format(self.project))
			je = frappe.new_doc("Journal Entry")
			je.voucher_type = "Journal Entry"
			je.naming_series = "JV-"
			je.posting_date = posting_date
			je.project = self.project 
			je.company = self.company
			je.business_unit = self.business_unit
			je.remark = "Journal Entry against import operation {0}".format(self.name)

			je.append("accounts", {
				"account": pj.project_account,
				"credit_in_account_currency": flt(pj.total_actual_cost),
				"business_unit": self.business_unit,
				"project": self.project, 
				"cost_center": cost_center
			})

			je.append("accounts", {
				"account": pj.project_closing_account,
				"debit_in_account_currency": flt(pj.total_actual_cost),
				"business_unit": self.business_unit,
				"project": self.project, 
				"cost_center": cost_center
			})

			je.flags.ignore_permissions = True
			je.submit()
			
			frappe.db.set_value("Project",self.project,"status","Completed")
			je_list.append(je.name)
			if je_list:
				message = ["""<a href="#Form/Journal Entry/%s" target="_blank">%s</a>""" % \
					(p, p) for p in je_list]
				frappe.msgprint(_("Journal Entry {0} created").format(comma_and(message)))
	
