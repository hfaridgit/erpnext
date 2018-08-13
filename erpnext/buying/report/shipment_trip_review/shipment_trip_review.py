# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns(filters)
	return columns, data

def get_filter_condition(filters):
	cond = ''
	if filters.get('exclude_completed') == 1:
		cond += " and ifnull(status,'')<>'Completed' "
	
	for f in filters:
		if f != 'exclude_completed':
			cond += " and " + f + " = '" + filters.get(f).replace("'", "\'") + "'"

	return cond

def get_data(filters):
	cond = get_filter_condition(filters)
	data = frappe.db.sql("""select company, business_unit, name, docstatus, ifnull(shipment_no,"___") as shipment_no, ifnull(status,'___') as status, supplier, purchase_order, 
									item_code, qty, ifnull(shipped_qty,"___") as shipped_qty, amount, currency, ifnull(destination_port,"___") as destination_port, 
									ifnull(expected_customs,"___") as expected_customs, ifnull(shipment_date,"___") as shipment_date,  
									ifnull(arrival_date,'___') as arrival_date, ifnull(docs_submition_date,'___') as docs_submition_date,    
									ifnull(acceptance_date,'___') as acceptance_date, datediff(acceptance_date,docs_submition_date) as bank_acceptance_duration,    
									ifnull(customs_start_date,'___') as customs_start_date, ifnull(customs_docs_date,'___') as customs_docs_date,    
									ifnull(samples_date,'___') as samples_date, ifnull(customs_release_date,'___') as customs_release_date, 
									datediff(customs_release_date,samples_date) as customs_release_duration, 
									ifnull(final_health_release_date,'___') as final_health_release_date, 
									datediff(final_health_release_date,arrival_date) as total_duration, 
									ifnull(customs_storage_charges,'___') as customs_storage_charges, ifnull(remarks,'___') as remarks 
									from `tabSupplier Shipment Trip`
									where 1=1 %s 
									order by shipment_no,purchase_order""" % (cond), as_dict=True)

	return data


def get_columns(filters):
	return [
		{
			"fieldname": "company",
			"label": _("company"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "business_unit",
			"label": _("business_unit"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "name",
			"label": _("name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "docstatus",
			"label": _("docstatus"),
			"fieldtype": "Int",
			"hidden": 1
		},
		{
			"fieldname": "shipment_no",
			"label": _("Shipment No."),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Link",
			"actualtype": "Select",
			"options": "HHH",
			"actualoptions": "Canceled,Completed",
			"width": 80
		},
		{
			"fieldname": "supplier",
			"label": _("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"actualtype": "",
			"actualoptions": "",
			"width": 150
		},
		{
			"fieldname": "purchase_order",
			"label": _("PO"),
			"fieldtype": "Link",
			"options": "Purchase Order",
			"actualtype": "",
			"actualoptions": "",
			"width": 120
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"width": 80
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency", 
			"width": 80
		},
		{
			"fieldname": "destination_port",
			"label": _("Destination Port"),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 120
		},
		{
			"fieldname": "expected_customs",
			"label": _("Expected Customs"),
			"fieldtype": "Link",
			"actualtype": "Currency",
			"options": "HHH",
			"actualoptions": "",
			"width": 120
		},
		{
			"fieldname": "shipment_date",
			"label": _("Shipment Date"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 110
		},
		{
			"fieldname": "arrival_date",
			"label": _("Arrival Date"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 80
		},
		{
			"fieldname": "docs_submition_date",
			"label": _("Bank Submition Date"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 150
		},
		{
			"fieldname": "acceptance_date",
			"label": _("Receive Docs From Bank"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 200
		},
		{
			"fieldname": "bank_acceptance_duration",
			"label": _("Bank Acceptance Duration"),
			"fieldtype": "Int",
			"width": 170
		}, 
		{
			"fieldname": "customs_start_date",
			"label": _("Send Docs for Clearance"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 200
		},
		{
			"fieldname": "customs_docs_date",
			"label": _("Customs Docs Date"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 130
		},
		{
			"fieldname": "samples_date",
			"label": _("Samples Date"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 100
		},
		{
			"fieldname": "customs_release_date",
			"label": _("Customs Release Date"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 150
		},
		{
			"fieldname": "customs_release_duration",
			"label": _("Customs Release Duration"),
			"fieldtype": "Int",
			"width": 170
		}, 
		{
			"fieldname": "final_health_release_date",
			"label": _("Final Health Release Date"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 170
		},
		{
			"fieldname": "total_duration",
			"label": _("Total Duration"),
			"fieldtype": "Int",
			"width": 100
		}, 
		{
			"fieldname": "customs_storage_charges",
			"label": _("Customs Storage Charges"),
			"fieldtype": "Link",
			"actualtype": "Currency",
			"options": "HHH",
			"actualoptions": "",
			"width": 170
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Link",
			"actualtype": "Text",
			"options": "HHH",
			"actualoptions": "",
			"width": 300
		},
	]

@frappe.whitelist()
def generate_data():
	frappe.db.sql("""insert ignore into `tabSupplier Shipment Trip` (`name`,  `creation`,  `modified`,  `modified_by`,  `owner`,  `docstatus`,  
					`company`,  `business_unit`, `purchase_order`,  `supplier`,  `amount`, `currency`)
					(select po.name, now(), now(), %(user)s, %(user)s, 0, 
					 po.company, po.business_unit, po.name, po.supplier, po.grand_total, po.currency 
					 from `tabPurchase Order` po 
					 where po.docstatus=1 and is_import=1)""", {"user": frappe.session.user})
