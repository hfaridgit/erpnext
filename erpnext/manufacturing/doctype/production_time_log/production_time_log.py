# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import time_diff_in_seconds
from frappe.model.document import Document

class ProductionTimeLog(Document):
	def get_operations(self):
		return frappe.db.sql("""select tsd.operation from `tabTimesheet Detail` tsd
								left join `tabTimesheet` ts on ts.name=tsd.parent
								where ts.docstatus=0 and ts.production_order=%s""", (self.production_order))

	def on_submit(self):
		ts = frappe.db.sql("""select ts.name from `tabTimesheet Detail` tsd
								left join `tabTimesheet` ts on ts.name=tsd.parent
								where ts.docstatus=0 and ts.production_order=%s and tsd.operation=%s""", (self.production_order, self.operation))
		
		if ts:
			tsh = frappe.get_doc("Timesheet", ts[0][0])
			for row in tsh.time_logs:
				if row.operation == self.operation:
					row.from_time = self.from_time
					row.to_time = self.to_time
					row.hours = time_diff_in_seconds(self.to_time, self.from_time)/3600
			tsh.save()
				