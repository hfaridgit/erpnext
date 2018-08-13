# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

from erpnext.manufacturing.doctype.production_order import production_order

class SampleRequest(Document):
	pass

@frappe.whitelist()
def make_production_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		conversion_factor = frappe.db.get_value('UOM Conversion Detail', {'parent': source.item_code, 'uom': 'Kg'}, 'conversion_factor')
		if conversion_factor:
			target.qty = flt(source.sample_weight) * flt(conversion_factor)

		target.production_item = source.item_code

		item_details = production_order.get_item_details(source.item_code)
		target.update(item_details)

		target.run_method('set_required_items')

	doclist = get_mapped_doc(
		'Sample Request',
		source_name,
		{
			'Sample Request': {
				'doctype': 'Production Order',
				'validation': { 'docstatus': ['=', 1] }
			}
		},
		target_doc,
		set_missing_values
	)

	return doclist
