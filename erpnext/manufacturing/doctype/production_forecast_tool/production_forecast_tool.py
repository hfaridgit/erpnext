# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, flt, cint, nowdate, add_days, comma_and

from frappe import msgprint, _

from frappe.model.document import Document
from erpnext.manufacturing.doctype.bom.bom import validate_bom_no
from erpnext.manufacturing.doctype.production_order.production_order import get_item_details

class ProductionForecastTool(Document):
	def clear_table(self, table_name):
		self.set(table_name, [])

	def validate_company(self):
		if not self.company:
			frappe.throw(_("Please enter Company"))

	def get_items(self):
		item_condition = ""
		if self.business_unit:
			item_condition = ' and sf.business_unit = "{0}"'.format(frappe.db.escape(self.business_unit))
		if self.from_month:
			item_condition = " and month(str_to_date(sfm.month,'%M'))>=month(str_to_date('{0}','%M'))".format(frappe.db.escape(self.from_month))
		if self.to_month:
			item_condition = " and month(str_to_date(sfm.month,'%M'))>=month(str_to_date('{0}','%M'))".format(frappe.db.escape(self.to_month))

		items = frappe.db.sql("""select sf.item_code, sf.uom, sum(sfm.qty) as pending_qty, sf.year as forecast_year, i.default_warehouse 
			from `tabSales Forecast Month` sfm
			left join `tabSales Forecast` sf on sf.name=sfm.parent
			left join `tabItem` i on i.name=sf.item_code
			where sf.year=%s and sf.company=%s %s group by item_code""", (self.get_items_for_year, self.company, item_condition), as_dict=1)

		self.add_items(items)

	def add_items(self, items):
		self.clear_table("items")
		for p in items:
			item_details = get_item_details(p['item_code'])
			pi = self.append('items', {})
			pi.item_code				= p['item_code']
			pi.description				= item_details and item_details.description or ''
			pi.stock_uom				= item_details and item_details.stock_uom or ''
			pi.bom_no					= item_details and item_details.bom_no or ''
			pi.planned_qty				= flt(p['pending_qty'])
			pi.pending_qty				= flt(p['pending_qty'])
			pi.forecast_year			= flt(p['forecast_year'])
			pi.warehouse				= flt(p['default_warehouse'])


	def validate_data(self):
		self.validate_company()
		for d in self.get('items'):
			if not d.bom_no:
				frappe.throw(_("Please select BOM for Item in Row {0}".format(d.idx)))
			else:
				validate_bom_no(d.item_code, d.bom_no)

			if not flt(d.planned_qty):
				frappe.throw(_("Please enter Planned Qty for Item {0} at row {1}").format(d.item_code, d.idx))

	def raise_production_orders(self):
		"""It will raise production order (Draft) for all distinct FG items"""
		self.validate_data()

		from erpnext.utilities.transaction_base import validate_uom_is_integer
		validate_uom_is_integer(self, "stock_uom", "planned_qty")

		items = self.get_production_items()

		pro_list = []
		frappe.flags.mute_messages = True

		for key in items:
			production_order = self.create_production_order(items[key])
			if production_order:
				pro_list.append(production_order)

		frappe.flags.mute_messages = False

		if pro_list:
			pro_list = ["""<a href="#Form/Production Order/%s" target="_blank">%s</a>""" % \
				(p, p) for p in pro_list]
			msgprint(_("{0} created").format(comma_and(pro_list)))
		else :
			msgprint(_("No Production Orders created"))

	def get_production_items(self):
		item_dict = {}
		for d in self.get("items"):
			item_details= {
				"production_item"		: d.item_code,
				"bom_no"				: d.bom_no,
				"description"			: d.description,
				"stock_uom"				: d.stock_uom,
				"company"				: self.company,
				"business_unit"			: self.business_unit,
				"wip_warehouse"			: "",
				"fg_warehouse"			: d.warehouse,
				"status"				: "Draft"
			}

			""" Club similar BOM and item for processing in case of Sales Orders """
			item_details.update({
				"qty": d.planned_qty
			})
			item_dict[(d.item_code, d.material_request_item, d.warehouse)] = item_details

		return item_dict

	def create_production_order(self, item_dict):
		"""Create production order. Called from Production Planning Tool"""
		from erpnext.manufacturing.doctype.production_order.production_order import OverProductionError, get_default_warehouse
		warehouse = get_default_warehouse()
		pro = frappe.new_doc("Production Order")
		pro.update(item_dict)
		pro.set_production_order_operations()
		if warehouse:
			pro.wip_warehouse = warehouse.get('wip_warehouse')
		if not pro.fg_warehouse:
			pro.fg_warehouse = warehouse.get('fg_warehouse')

		try:
			pro.insert()
			return pro.name
		except OverProductionError:
			pass

	def get_forecast_wise_planned_qty(self):
		"""
			bom_dict {
				bom_no: ['forecast_year', 'qty']
			}
		"""
		bom_dict = {}
		for d in self.get("items"):
			bom_dict.setdefault(d.bom_no, []).append([d.forecast_year, flt(d.planned_qty)])
		return bom_dict

	def download_raw_materials(self):
		""" Create csv data for required raw material to produce finished goods"""
		self.validate_data()
		bom_dict = self.get_forecast_wise_planned_qty()
		self.get_raw_materials(bom_dict)
		return self.get_csv()

	def get_raw_materials(self, bom_dict,non_stock_item=0):
		""" Get raw materials considering sub-assembly items
			{
				"item_code": [qty_required, description, stock_uom, min_order_qty]
			}
		"""
		item_list = []
		precision = frappe.get_precision("BOM Item", "stock_qty")

		for bom, so_wise_qty in bom_dict.items():
			bom_wise_item_details = {}
			if self.use_multi_level_bom and self.only_raw_materials and self.include_subcontracted:
				# get all raw materials with sub assembly childs
				# Did not use qty_consumed_per_unit in the query, as it leads to rounding loss
				for d in frappe.db.sql("""select fb.item_code,
					ifnull(sum(fb.stock_qty/ifnull(bom.quantity, 1)), 0) as qty,
					fb.description, fb.stock_uom, item.min_order_qty
					from `tabBOM Explosion Item` fb, `tabBOM` bom, `tabItem` item
					where bom.name = fb.parent and item.name = fb.item_code
					and (item.is_sub_contracted_item = 0 or ifnull(item.default_bom, "")="")
					""" + ("and item.is_stock_item = 1","")[non_stock_item] + """
					and fb.docstatus<2 and bom.name=%(bom)s
					group by fb.item_code, fb.stock_uom""", {"bom":bom}, as_dict=1):
						bom_wise_item_details.setdefault(d.item_code, d)
			else:
				# Get all raw materials considering SA items as raw materials,
				# so no childs of SA items
				bom_wise_item_details = self.get_subitems(bom_wise_item_details, bom,1, \
					self.use_multi_level_bom,self.only_raw_materials, self.include_subcontracted,non_stock_item)

			for item, item_details in bom_wise_item_details.items():
				for so_qty in so_wise_qty:
					item_list.append([item, flt(flt(item_details.qty) * so_qty[1], precision),
						item_details.description, item_details.stock_uom, item_details.min_order_qty,
						so_qty[0]])

		self.make_items_dict(item_list)

	def get_subitems(self,bom_wise_item_details, bom, parent_qty, include_sublevel, only_raw, supply_subs,non_stock_item=0):
		items = frappe.db.sql("""
			SELECT
				bom_item.item_code,
				default_material_request_type,
				ifnull(%(parent_qty)s * sum(bom_item.stock_qty/ifnull(bom.quantity, 1)), 0) as qty,
				item.is_sub_contracted_item as is_sub_contracted,
				item.default_bom as default_bom,
				bom_item.description as description,
				bom_item.stock_uom as stock_uom,
				item.min_order_qty as min_order_qty
			FROM
				`tabBOM Item` bom_item,
				`tabBOM` bom,
				tabItem item
			where
				bom.name = bom_item.parent
				and bom.name = %(bom)s
				and bom_item.docstatus < 2
				and bom_item.item_code = item.name
			""" + ("and item.is_stock_item = 1", "")[non_stock_item] + """
			group by bom_item.item_code""", {"bom": bom, "parent_qty": parent_qty}, as_dict=1)

		for d in items:
			if ((d.default_material_request_type == "Purchase"
				and not (d.is_sub_contracted and only_raw and include_sublevel))
				or (d.default_material_request_type == "Manufacture" and not only_raw)):

				if d.item_code in bom_wise_item_details:
					bom_wise_item_details[d.item_code].qty = bom_wise_item_details[d.item_code].qty + d.qty
				else:
					bom_wise_item_details[d.item_code] = d

			if include_sublevel and d.default_bom:
				if ((d.default_material_request_type == "Purchase" and d.is_sub_contracted and supply_subs)
					or (d.default_material_request_type == "Manufacture")):

					my_qty = 0
					projected_qty = self.get_item_projected_qty(d.item_code)
					if self.create_material_requests_for_all_required_qty:
						my_qty = d.qty
					else:
						total_required_qty = flt(bom_wise_item_details.get(d.item_code, frappe._dict()).qty)
						if (total_required_qty - d.qty) < projected_qty:
							my_qty = total_required_qty - projected_qty
						else:
							my_qty = d.qty

					if my_qty > 0:
						self.get_subitems(bom_wise_item_details,
							d.default_bom, my_qty, include_sublevel, only_raw, supply_subs)

		return bom_wise_item_details

	def make_items_dict(self, item_list):
		if not getattr(self, "item_dict", None):
			self.item_dict = {}

		for i in item_list:
			self.item_dict.setdefault(i[0], []).append([flt(i[1]), i[2], i[3], i[4], i[5]])

	def get_csv(self):
		item_list = [['Item Code', 'Description', 'Stock UOM', 'Required Qty', 'Warehouse',
		 	'Quantity Requested for Purchase', 'Ordered Qty', 'Actual Qty']]
		for item in self.item_dict:
			total_qty = sum([flt(d[0]) for d in self.item_dict[item]])
			item_list.append([item, self.item_dict[item][0][1], self.item_dict[item][0][2], total_qty])
			item_qty = frappe.db.sql("""select warehouse, indented_qty, ordered_qty, actual_qty
				from `tabBin` where item_code = %s""", item, as_dict=1)

			i_qty, o_qty, a_qty = 0, 0, 0
			for w in item_qty:
				i_qty, o_qty, a_qty = i_qty + flt(w.indented_qty), o_qty + \
					flt(w.ordered_qty), a_qty + flt(w.actual_qty)

				item_list.append(['', '', '', '', w.warehouse, flt(w.indented_qty),
					flt(w.ordered_qty), flt(w.actual_qty)])
			if item_qty:
				item_list.append(['', '', '', '', 'Total', i_qty, o_qty, a_qty])
			else:
				item_list.append(['', '', '', '', 'Total', 0, 0, 0])

		return item_list

	def raise_material_requests(self):
		"""
			Raise Material Request if projected qty is less than qty required
			Requested qty should be shortage qty considering minimum order qty
		"""
		self.validate_data()
		if not self.purchase_request_for_warehouse:
			frappe.throw(_("Please enter Warehouse for which Material Request will be raised"))

		bom_dict = self.get_forecast_wise_planned_qty()
		self.get_raw_materials(bom_dict,self.create_material_requests_non_stock_request)

		if self.item_dict:
			self.create_material_request()

	def get_requested_items(self):
		items_to_be_requested = frappe._dict()

		if not self.create_material_requests_for_all_required_qty:
			item_projected_qty = self.get_projected_qty()

		for item, so_item_qty in self.item_dict.items():
			total_qty = sum([flt(d[0]) for d in so_item_qty])
			requested_qty = 0

			if self.create_material_requests_for_all_required_qty:
				requested_qty = total_qty
			elif total_qty > item_projected_qty.get(item, 0):
				# shortage
				requested_qty = total_qty - flt(item_projected_qty.get(item))
				# consider minimum order qty

			if requested_qty and requested_qty < flt(so_item_qty[0][3]):
				requested_qty = flt(so_item_qty[0][3])

			# distribute requested qty SO wise
			for item_details in so_item_qty:
				if requested_qty:
					sales_order = item_details[4] or "No Sales Order"
					if self.get_items_from == "Material Request":
						sales_order = "No Sales Order"
					if requested_qty <= item_details[0]:
						adjusted_qty = requested_qty
					else:
						adjusted_qty = item_details[0]

					items_to_be_requested.setdefault(item, {}).setdefault(sales_order, 0)
					items_to_be_requested[item][sales_order] += adjusted_qty
					requested_qty -= adjusted_qty
				else:
					break

			# requested qty >= total so qty, due to minimum order qty
			if requested_qty:
				items_to_be_requested.setdefault(item, {}).setdefault("No Sales Order", 0)
				items_to_be_requested[item]["No Sales Order"] += requested_qty

		return items_to_be_requested

	def get_item_projected_qty(self,item):
		conditions = ""
		if self.purchase_request_for_warehouse:
			conditions = " and warehouse='{0}'".format(frappe.db.escape(self.purchase_request_for_warehouse))

		item_projected_qty = frappe.db.sql("""
			select ifnull(sum(projected_qty),0) as qty
			from `tabBin`
			where item_code = %(item_code)s {conditions}
		""".format(conditions=conditions), { "item_code": item }, as_dict=1)

		return item_projected_qty[0].qty

	def get_projected_qty(self):
		items = self.item_dict.keys()
		item_projected_qty = frappe.db.sql("""select item_code, sum(projected_qty)
			from `tabBin` where item_code in (%s) and warehouse=%s group by item_code""" %
			(", ".join(["%s"]*len(items)), '%s'), tuple(items + [self.purchase_request_for_warehouse]))

		return dict(item_projected_qty)

	def create_material_request(self):
		items_to_be_requested = self.get_requested_items()

		material_request_list = []
		if items_to_be_requested:
			for item in items_to_be_requested:
				item_wrapper = frappe.get_doc("Item", item)
				material_request = frappe.new_doc("Material Request")
				material_request.update({
					"transaction_date": nowdate(),
					"status": "Draft",
					"company": self.company,
					"business_unit": self.business_unit,
					"requested_by": frappe.session.user,
					"schedule_date": add_days(nowdate(), cint(item_wrapper.lead_time_days)),
				})
				material_request.update({"material_request_type": item_wrapper.default_material_request_type})

				for sales_order, requested_qty in items_to_be_requested[item].items():
					material_request.append("items", {
						"doctype": "Material Request Item",
						"__islocal": 1,
						"item_code": item,
						"item_name": item_wrapper.item_name,
						"description": item_wrapper.description,
						"uom": item_wrapper.stock_uom,
						"item_group": item_wrapper.item_group,
						"brand": item_wrapper.brand,
						"qty": requested_qty,
						"schedule_date": add_days(nowdate(), cint(item_wrapper.lead_time_days)),
						"warehouse": self.purchase_request_for_warehouse,
						"sales_order": sales_order if sales_order!="No Sales Order" else None,
						"project": frappe.db.get_value("Sales Order", sales_order, "project") \
							if sales_order!="No Sales Order" else None
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
