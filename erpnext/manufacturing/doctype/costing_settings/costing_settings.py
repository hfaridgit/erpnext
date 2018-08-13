# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CostingSettings(Document):
	def on_update(self):
		ws_list = frappe.db.sql("""select name from `tabWorkstation`""", )

		for ws in ws_list:
			w = frappe.get_doc("Workstation", ws[0])
			w.save()
			
