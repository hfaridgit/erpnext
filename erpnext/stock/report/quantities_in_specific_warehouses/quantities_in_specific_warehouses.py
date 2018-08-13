# -*- coding: utf-8 -*-
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

parent_warehouses = ['مخزن رئيسى - M', 'تحت الفحص - M', 'مرتجعات - M']

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns = []

	for warehouse in parent_warehouses:
		columns.append(warehouse + ':Float:160')

	columns.append(_('Total') + ':Float:160')
	columns.insert(0, _('Item') + ':Link/Item:240')
	return columns

def get_data(filters):
	data = []
	items = get_items(filters)

	for item in items:
		row = []

		for warehouse in parent_warehouses:
			row.append(get_quantity(item.item_code, warehouse))

		row.append(sum(row))
		row.insert(0, item.item_code)
		data.append(tuple(row))

	return data

def get_items(filters):
	conditions = "WHERE item_code = '{0}'".format(filters.item_code) if filters.get('item_code') else ''

	return frappe.db.sql(
		"SELECT item_code FROM `tabBin` {0} group by item_code ORDER BY item_code".format(conditions),
		filters,
		as_dict=True
	)

def get_quantity(item_code, warehouse):
	warehouses = frappe.db.sql(
		"SELECT name FROM `tabWarehouse` WHERE parent_warehouse = %s",
		warehouse,
		as_list=True
	)

	quantities = frappe.db.sql(
		"""
		SELECT SUM(actual_qty) AS 'actual_qty' FROM `tabBin`
		WHERE item_code = %s AND warehouse IN ({0})
		GROUP BY item_code
		""".format(', '.join(['%s'] * len(warehouses))),
		[item_code] + warehouses
	)

	if quantities and quantities[0] and quantities[0][0]:
		return quantities[0][0]

	return 0.0
