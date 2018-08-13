# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now
from frappe.model.document import Document

class ProductionTimeLogTool(Document):
	def get_operations(self):
		return frappe.db.sql("""select tsd.operation from `tabTimesheet Detail` tsd
								left join `tabTimesheet` ts on ts.name=tsd.parent
								where ts.docstatus=0 and ts.production_order=%s""", (self.production_order))

	def get_times(self):
		times = frappe.db.sql("""select docstatus, if(isnull(from_time),0,1) as from_time, if(isnull(to_time),0,1) as to_time from `tabProduction Time Log` 
								where docstatus<2 and production_order=%s and operation=%s
								order by docstatus DESC Limit 1""", (self.production_order, self.operation), as_dict=1)
		
		return times
		
	def register_start(self):
		pt = frappe.db.sql("""select name from `tabProduction Time Log` 
				where production_order=%s and operation=%s and docstatus=0""", (self.production_order, self.operation), as_dict=1)
		if not pt:
			ptl = frappe.new_doc("Production Time Log")
			ptl.update({
				"production_order": self.production_order,
				"operation": self.operation,
				"from_time": now()
			})
			ptl.insert()
		else:
			ptl = frappe.get_doc("Production Time Log", pt[0].name)
			ptl.update({"from_time": now()})
			ptl.save()

	def register_end(self):
		pt = frappe.db.sql("""select name from `tabProduction Time Log` 
				where production_order=%s and operation=%s and docstatus=0""", (self.production_order, self.operation), as_dict=1)
		if not pt:
			ptl = frappe.new_doc("Production Time Log")
			ptl.update({
				"production_order": self.production_order,
				"operation": self.operation,
				"to_time": now()
			})
			ptl.insert()
		else:
			ptl = frappe.get_doc("Production Time Log", pt[0].name)
			ptl.update({"to_time": now()})
			ptl.save()
			
		ptl.submit()
			
		