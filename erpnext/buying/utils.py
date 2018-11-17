# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr, cint
from frappe import _
import json

from erpnext.stock.doctype.item.item import get_last_purchase_details
from erpnext.stock.doctype.item.item import validate_end_of_life

def update_last_purchase_rate(doc, is_submit):
	"""updates last_purchase_rate in item table for each item"""

	import frappe.utils
	this_purchase_date = frappe.utils.getdate(doc.get('posting_date') or doc.get('transaction_date'))

	for d in doc.get("items"):
		# get last purchase details
		last_purchase_details = get_last_purchase_details(d.item_code, doc.name)

		# compare last purchase date and this transaction's date
		last_purchase_rate = None
		if last_purchase_details and \
				(last_purchase_details.purchase_date > this_purchase_date):
			last_purchase_rate = last_purchase_details['base_rate']
		elif is_submit == 1:
			# even if this transaction is the latest one, it should be submitted
			# for it to be considered for latest purchase rate
			if flt(d.conversion_factor):
				last_purchase_rate = flt(d.base_rate) / flt(d.conversion_factor)
			else:
				frappe.throw(_("UOM Conversion factor is required in row {0}").format(d.idx))

		# update last purchsae rate
		if last_purchase_rate:
			frappe.db.sql("""update `tabItem` set last_purchase_rate = %s where name = %s""",
				(flt(last_purchase_rate), d.item_code))

def validate_for_items(doc):
	items = []
	for d in doc.get("items"):
		if not d.qty:
			if doc.doctype == "Purchase Receipt" and d.rejected_qty:
				continue
			frappe.throw(_("Please enter quantity for Item {0}").format(d.item_code))

		# update with latest quantities
		bin = frappe.db.sql("""select projected_qty from `tabBin` where
			item_code = %s and warehouse = %s""", (d.item_code, d.warehouse), as_dict=1)

		f_lst ={'projected_qty': bin and flt(bin[0]['projected_qty']) or 0, 'ordered_qty': 0, 'received_qty' : 0}
		if d.doctype in ('Purchase Receipt Item', 'Purchase Invoice Item'):
			f_lst.pop('received_qty')
		for x in f_lst :
			if d.meta.get_field(x):
				d.set(x, f_lst[x])

		item = frappe.db.sql("""select is_stock_item,
			is_sub_contracted_item, end_of_life, disabled from `tabItem` where name=%s""",
			d.item_code, as_dict=1)[0]

		validate_end_of_life(d.item_code, item.end_of_life, item.disabled)

		# validate stock item
		if item.is_stock_item==1 and d.qty and not d.warehouse and not d.get("delivered_by_supplier"):
			frappe.throw(_("Warehouse is mandatory for stock Item {0} in row {1}").format(d.item_code, d.idx))

		items.append(cstr(d.item_code))

	if items and len(items) != len(set(items)) and \
		not cint(frappe.db.get_single_value("Buying Settings", "allow_multiple_items") or 0):
		frappe.throw(_("Same item cannot be entered multiple times."))

def check_for_closed_status(doctype, docname):
	status = frappe.db.get_value(doctype, docname, "status")

	if status == "Closed":
		frappe.throw(_("{0} {1} status is {2}").format(doctype, docname, status), frappe.InvalidStatusError)
		
def validate_approved_items(ref_doc, supplier):
	b = frappe.get_doc("Buying Settings", "Buying Settings")
	if b.is_raw_material==1 or b.is_packing_material==1 or b.is_semi_product==1 or b.is_finished_product==1 or b.is_spare_part==1:
		if b.is_raw_material==1:
			approved_rm = frappe.db.sql_list("""select s.parent as item_code from `tabItem Supplier` s 
								left join `tabItem` i on i.name=s.parent 
								where i.is_raw_material=%s and s.parenttype='Item' 
								and s.docstatus<2 and s.supplier=%s""", (b.is_raw_material, supplier))

		if b.is_packing_material==1:
			approved_pk = frappe.db.sql_list("""select s.parent as item_code from `tabItem Supplier` s 
								left join `tabItem` i on i.name=s.parent 
								where i.is_packing_material=%s and s.parenttype='Item' 
								and s.docstatus<2 and s.supplier=%s""", (b.is_packing_material, supplier))

		if b.is_semi_product==1:
			approved_sf = frappe.db.sql_list("""select s.parent as item_code from `tabItem Supplier` s 
								left join `tabItem` i on i.name=s.parent 
								where i.is_semi_product=%s and s.parenttype='Item' 
								and s.docstatus<2 and s.supplier=%s""", (b.is_semi_product, supplier))

		if b.is_finished_product==1:
			approved_fp = frappe.db.sql_list("""select s.parent as item_code from `tabItem Supplier` s 
								left join `tabItem` i on i.name=s.parent 
								where i.is_finished_product=%s and s.parenttype='Item' 
								and s.docstatus<2 and s.supplier=%s""", (b.is_finished_product, supplier))
		if b.is_spare_part==1:
			approved_sp = frappe.db.sql_list("""select s.parent as item_code from `tabItem Supplier` s 
								left join `tabItem` i on i.name=s.parent 
								where i.is_spare_part=%s and s.parenttype='Item' 
								and s.docstatus<2 and s.supplier=%s""", (b.is_spare_part, supplier))
		
		x = 0
		for item in ref_doc.items:
			if b.is_raw_material==1: 
				is_rm = frappe.get_value("Item", item.item_code, "is_raw_material")
				if is_rm==1 and not approved_rm:
					x = 1
					frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
				if approved_rm:
					if is_rm==1 and item.item_code not in approved_rm:
						x = 1
						frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
					
			if b.is_packing_material==1: 
				is_pk = frappe.get_value("Item", item.item_code, "is_packing_material")
				if is_pk==1 and not approved_pk:
					x = 1
					frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
				if approved_pk:
					if is_pk==1 and item.item_code not in approved_pk:
						x = 1
						frappe.msgprint(_("Item {0} at row {1} not in PK approved list for supplier {2}").format(item.item_code, item.idx, supplier))
					
			if b.is_semi_product==1: 
				is_sf = frappe.get_value("Item", item.item_code, "is_semi_product")
				if is_sf==1 and not approved_sf:
					x = 1
					frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
				if approved_sf:
					if is_sf==1 and item.item_code not in approved_sf:
						x = 1
						frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
					
			if b.is_finished_product==1:
				is_fp = frappe.get_value("Item", item.item_code, "is_finished_product")
				if is_fp==1 and not approved_fp:
					x = 1
					frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
				if approved_fp:
					if is_fp==1 and item.item_code not in approved_fp:
						x = 1
						frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
					
			if b.is_spare_part==1: 
				is_sp = frappe.get_value("Item", item.item_code, "is_spare_part")
				if is_sp==1 and not approved_sp:
					x = 1
					frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
				if approved_sp:
					if is_sp==1 and item.item_code not in approved_sp:
						x = 1
						frappe.msgprint(_("Item {0} at row {1} not in approved list for supplier {2}").format(item.item_code, item.idx, supplier))
				
		if x == 1:
			frappe.throw(_("Please Choose Approved Items Only."))

@frappe.whitelist()
def get_linked_material_requests(items):
	items = json.loads(items)
	mr_list = []
	for item in items:
		material_request = frappe.db.sql("""SELECT distinct mr.name AS mr_name, 
				(mr_item.qty - mr_item.ordered_qty) AS qty, 
				mr_item.item_code AS item_code,
				mr_item.name AS mr_item 
			FROM `tabMaterial Request` mr, `tabMaterial Request Item` mr_item
			WHERE mr.name = mr_item.parent
				AND mr_item.item_code = %(item)s 
				AND mr.material_request_type = 'Purchase'
				AND mr.per_ordered < 99.99
				AND mr.docstatus = 1
				AND mr.status != 'Stopped'
                        ORDER BY mr_item.item_code ASC""",{"item": item}, as_dict=1)
		if material_request:
			mr_list.append(material_request)
	
	return mr_list

