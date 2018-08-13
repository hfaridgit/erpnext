# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import json
import six

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, flt

from erpnext.manufacturing.doctype.production_order import production_order

class SampleRequest(Document):
	def before_submit(self):
		self.has_enough_qty_on_submit = cint(has_enough_qty(self))

@frappe.whitelist()
def has_enough_qty(doc):
	if isinstance(doc, six.string_types):
		doc = frappe._dict(json.loads(doc))

	conversion_factor = frappe.db.get_value('UOM Conversion Detail', {'parent': doc.item_code, 'uom': 'Kg'}, 'conversion_factor')

	bin = frappe.db.sql(
		"SELECT SUM(actual_qty) AS 'actual_qty' FROM `tabBin` WHERE item_code = %(item_code)s GROUP BY item_code",
		{'item_code': doc.item_code},
		as_dict=True
	)

	if conversion_factor and bin:
		return flt(doc.sample_weight) * flt(conversion_factor) <= flt(bin[0].actual_qty)

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
