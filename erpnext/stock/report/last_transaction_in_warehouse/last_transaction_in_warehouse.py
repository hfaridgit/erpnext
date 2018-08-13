# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	validate_filters(filters)

	return get_columns(filters), get_data(filters)

def validate_filters(filters):
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if not filters.get("to_date"):
		frappe.throw(_("'To Date' is required"))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_columns(filters):
	return [
		_('Item') + ':Link/Item:120',
		_('Item Name') + '::160',
		_('Item Group') + ':Link/Item Group:120',
		_('Warehouse') + ':Link/Warehouse:120',
		_('Warehouse Name') + '::160',
		_('Warehouse Group') + ':Link/Warehouse:120',
		_('Actual Qty') + ':Float:',
		_('Last Transaction Date') + ':Date:'
	]

def get_data(filters):
	return frappe.db.sql(
		"""
			SELECT ltiw.* FROM(
				SELECT
					b.item_code,
					i.item_name,
					i.item_group,
					b.warehouse,
					w.warehouse_name,
					w.parent_warehouse,
					b.actual_qty,
					(
						SELECT sle.posting_date FROM `tabStock Ledger Entry` AS `sle`
						WHERE sle.item_code = b.item_code
						AND sle.warehouse = b.warehouse
						ORDER BY sle.posting_date DESC, sle.posting_time DESC
						LIMIT 1
					) AS 'posting_date'
				FROM `tabBin` AS `b`
				LEFT JOIN `tabItem` AS `i` ON i.name = b.item_code
				LEFT JOIN `tabWarehouse` AS `w` ON w.name = b.warehouse
				{0}
			) AS `ltiw`
			WHERE ltiw.posting_date BETWEEN %(from_date)s AND %(to_date)s
			ORDER BY ltiw.item_code, ltiw.warehouse
		""".format(get_conditions(filters)),
		filters
	)

def get_conditions(filters):
	conditions = "WHERE TRUE"

	if filters.get('item_code'):
		conditions += " AND b.item_code = %(item_code)s"

	if filters.get('uom'):
		conditions += " AND i.stock_uom = %(uom)s"

	if filters.get('warehouse_group'):
		conditions += " AND w.parent_warehouse = %(warehouse_group)s"

	if filters.get('warehouse'):
		conditions += " AND b.warehouse = %(warehouse)s"

	return conditions
