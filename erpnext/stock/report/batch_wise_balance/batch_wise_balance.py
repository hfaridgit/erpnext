# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import get_match_cond

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	return [
		_('Item') + ':Link/Item:120',
		_('Item Name') + '::160',
		_('Batch') + ':Link/Batch:120',
		_('Warehouse') + ':Link/Warehouse:120',
		_('Qty') + ':Float:'
	]

def get_data(filters):
	return frappe.db.sql(
		"""
			SELECT
				sle.item_code AS 'item_code',
				i.item_name AS 'item_name',
				sle.batch_no AS 'batch_no',
				sle.warehouse AS 'warehouse',
				SUM(sle.actual_qty) AS 'actual_qty'
			FROM `tabStock Ledger Entry` AS `sle`
			LEFT JOIN `tabItem` AS `i` ON i.name = sle.item_code
			{0}
			GROUP BY sle.batch_no, sle.warehouse
			ORDER BY sle.item_code, sle.batch_no, sle.warehouse
		""".format(get_conditions(filters)),
		filters
	)

def get_conditions(filters):
	conditions = "WHERE sle.batch_no IS NOT NULL"
	conditions += get_match_cond('Warehouse')

	if filters.get('item_code'):
		conditions += " AND sle.item_code = %(item_code)s"

	return conditions
