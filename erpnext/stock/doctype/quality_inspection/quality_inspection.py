# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe


from frappe.model.document import Document

class QualityInspection(Document):
	def validate(self):
		from erpnext.setup.doctype.business_unit.business_unit import validate_bu
		validate_bu(self)
		
		self.put_in_reference()
	
	def get_item_specification_details(self):
		self.set('readings', [])
		variant_of = frappe.db.get_value("Item", self.item_code, "variant_of")
		specification = None
		if variant_of:
			specification = frappe.db.sql("select specification, value from `tabItem Quality Inspection Parameter` \
				where parent in (%s, %s) order by idx", (self.item_code, variant_of))
		else:
			specification = frappe.db.sql("select specification, value from `tabItem Quality Inspection Parameter` \
				where parent = %s order by idx", self.item_code)
		if not specification:
			if self.item_code:
				is_rm, is_pm, is_sp, is_fp = frappe.db.get_value('Item', self.item_code, ['is_raw_material', 'is_packing_material', 'is_semi_product', 'is_finished_product'])
				if is_rm == 1:
					specification = frappe.db.sql("select specification, value from `tabQuality Inspection Parameters` \
						where is_raw_material=%s order by idx", (is_rm))
				if is_pm == 1:
					specification = frappe.db.sql("select specification, value from `tabQuality Inspection Parameters` \
						where is_packing_material=%s order by idx", (is_pm))
				if is_sp == 1:
					specification = frappe.db.sql("select specification, value from `tabQuality Inspection Parameters` \
						where is_semi_product=%s order by idx", (is_sp))
				if is_fp == 1:
					specification = frappe.db.sql("select specification, value from `tabQuality Inspection Parameters` \
						where is_finished_product=%s order by idx", (is_fp))
		
		for d in specification:
			child = self.append('readings', {})
			child.specification = d[0]
			child.value = d[1]
			child.status = 'Accepted'

	def on_submit(self):
		self.put_in_reference()
	
	def put_in_reference(self):
		if self.reference_type and self.reference_name:
			frappe.db.sql("""update `tab{doctype} {child_suffix}` t1, `tab{doctype}` t2
				set t1.quality_inspection = %s, t2.modified = %s
				where t1.parent = %s and t1.item_code = %s and t1.batch_no = %s and t1.parent = t2.name"""
				.format(
					doctype=self.reference_type,
					child_suffix = "Item" if self.reference_type != "Stock Entry" else "Detail"
				),
				(self.name, self.modified, self.reference_name, self.item_code, self.batch_no))
				
	def on_cancel(self):
		self.remove_from_reference
		
	def on_trash(self):
		self.remove_from_reference
		
	def remove_from_reference(self):
		if self.reference_type and self.reference_name:
			frappe.db.sql("""update `tab{doctype} {child_suffix}` 
				set quality_inspection = null, modified=%s 
				where quality_inspection = %s"""
				.format(
					doctype=self.reference_type,
					child_suffix = "Item" if self.reference_type != "Stock Entry" else "Detail"
				),
				(self.modified, self.name))
				
	def get_last_parameters(self):
		return frappe.db.sql("""select * from `tabQuality Inspection` where docstatus=1 and item_code=%s 
								order by report_date desc limit 1""", (self.item_code), as_dict=1)
		
			
def item_query(doctype, txt, searchfield, start, page_len, filters):
	if filters.get("from"):
		from frappe.desk.reportview import get_match_cond
		filters.update({
			"txt": txt,
			"mcond": get_match_cond(filters["from"]),
			"start": start,
			"page_len": page_len
		})
		return frappe.db.sql("""select item_code from `tab%(from)s`
			where parent='%(parent)s' and docstatus < 2 and item_code like '%%%(txt)s%%' %(mcond)s
			order by item_code limit %(start)s, %(page_len)s""" % filters)
