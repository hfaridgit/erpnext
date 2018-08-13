# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and

from frappe import msgprint, _

from frappe.model.document import Document
from erpnext.manufacturing.doctype.bom.bom import validate_bom_no
from erpnext.manufacturing.doctype.production_order.production_order import get_item_details

class MaterialsPlanningTool(Document):
	def clear_table(self, table_name):
		self.set(table_name, [])

	def validate_company(self):
		if not self.company:
			frappe.throw(_("Please enter Company"))
		if not self.business_unit:
			frappe.throw(_("Please enter Business Unit"))

	def get_open_production_orders(self):
		""" Pull production orders  which are pending"""
		po_filter = item_filter = ""
		if self.from_date:
			po_filter += " and po.planned_start_date >= %(from_date)s"
		if self.to_date:
			po_filter += " and po.planned_start_date <= %(to_date)s"

		if self.fg_item:
			item_filter += " and po.production_item = %(item)s"

		open_po = frappe.db.sql("""
			select distinct po.name, po.planned_start_date, po.production_item, po.description, po.bom_no, po.fg_warehouse as warehouse,
			(po.qty - po.produced_qty) as pending_qty
			from `tabProduction Order` po
			where po.docstatus = 1 and po.status not in ("Stopped", "Completed")
				and po.company = %(company)s and po.business_unit = %(business_unit)s 
				and po.qty > po.produced_qty {0} {1}
				and (exists (select name from `tabBOM` bom where bom.item=po.production_item
						and bom.is_active = 1))
			""".format(po_filter, item_filter), {
				"from_date": self.from_date,
				"to_date": self.to_date,
				"item": self.fg_item,
				"business_unit": self.business_unit, 
				"company": self.company
			}, as_dict=1)

		self.add_po_in_table(open_po)

	def add_po_in_table(self, open_po):
		""" Add production orders in the table"""
		self.clear_table("production_orders")

		po_list = []
		for r in open_po:
			if cstr(r['name']) not in po_list:
				pp_po = self.append('production_orders', {})
				pp_po.production_order = r['name']
				pp_po.planned_start_date = cstr(r['planned_start_date'])
				pp_po.production_item = r['production_item']
				pp_po.description = r['description']
				pp_po.pending_qty = flt(r['pending_qty'])
				pp_po.bom_no = r['bom_no']
				pp_po.warehouse = r['warehouse']


	def get_po_items(self):
		po_list = [d.production_order for d in self.get('production_orders') if d.production_order]
		if not po_list:
			msgprint(_("Please enter Production Orders in the above table"))
			return []

		item_condition = ""
		if self.fg_item:
			item_condition = ' and po.production_item = "{0}"'.format(frappe.db.escape(self.fg_item))

		items = frappe.db.sql("""select distinct poi.item_code, poi.description, po.buffer_warehouse,
			sum(poi.required_qty*(po.qty - po.produced_qty)/po.qty) as pending_qty
			from `tabProduction Order Item` poi
			left join `tabProduction Order` po on po.name=poi.parent
			where poi.parent in (%s)
			and exists (select name from `tabBOM` bom where bom.item=po.production_item
					and bom.is_active = 1) %s
			group by item_code, buffer_warehouse""" % \
			(", ".join(["%s"] * len(po_list)), item_condition), tuple(po_list), as_dict=1)

		self.add_items(items)

	def add_items(self, items):
		self.clear_table("items")
		for p in items:
			item_details = get_item_details(p.item_code)
			
			if item_details:
				pi = self.append('items', {})
				pi.warehouse				= p['buffer_warehouse']
				pi.item_code				= p['item_code']
				pi.description				= item_details[0] and item_details[0].description or ''
				pi.stock_uom				= item_details[0] and item_details[0].stock_uom or ''
				pi.pending_qty				= flt(p['pending_qty'])

	def validate_data(self):
		self.validate_company()
		
	def raise_material_requests(self):
		"""
			Raise Material Request if projected qty is less than qty required
			Requested qty should be shortage qty considering minimum order qty
		"""
		self.validate_data()
		self.create_material_request()

	def create_material_request(self):
		material_request_list = []
		if self.items:
			material_request = frappe.new_doc("Material Request")
			material_request.update({
				"naming_series": "_MRP-", 
				"planned_start_date": nowdate(),
				"status": "Draft",
				"company": self.company,
				"business_unit": self.business_unit,
				"requested_by": frappe.session.user,
				"schedule_date": self.requested_by_date,
				"material_request_type": "Material Transfer",
			})
			for item in self.items:
				item_wrapper = frappe.get_doc("Item", item.item_code)
				material_request.append("items", {
					"doctype": "Material Request Item",
					"__islocal": 1,
					"item_code": item.item_code,
					"item_name": item_wrapper.item_name,
					"description": item_wrapper.description,
					"uom": item_wrapper.stock_uom,
					"item_group": item_wrapper.item_group,
					"brand": item_wrapper.brand,
					"business_unit": self.business_unit,
					"qty": item.pending_qty,
					"schedule_date": self.requested_by_date,
					"warehouse": item.warehouse,
				})

			material_request.flags.ignore_permissions = 1
			material_request.submit()
			material_request_list.append(material_request.name)

			if material_request_list:
				message = ["""<a href="#Form/Material Request/%s" target="_blank">%s</a>""" % \
					(p, p) for p in material_request_list]
				msgprint(_("Material Requests {0} created").format(comma_and(message)))
		else:
			msgprint(_("Nothing to request"))

@frappe.whitelist()
def get_item_details(item):
	return frappe.db.sql("""select stock_uom, description from `tabItem`
											where disabled=0
												and (end_of_life is null or end_of_life='0000-00-00' or end_of_life > %s)
												and name=%s""", (nowdate(), item), as_dict=1)

