# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	return [
		_('Month') + '::',
		_('Item') + ':Link/Item:120',
		_('Item Name') + '::160',
		_('Qty') + ':Float:',
		_('UOM') + ':Link/UOM:',
		_('Last Year Forecast Qty') + ':Float:160',
		_('Last Year Actual Qty') + ':Float:160',
		_('Company') + ':Link/Company:',
		_('Business Unit') + ':Link/Business Unit:120'
	]

def get_data(filters):
	return frappe.db.sql(
		"""
			SELECT
				sfm.month AS 'month',
				sf.item_code AS 'item_code',
				sf.item_name AS 'item_name',
				SUM(sfm.qty) AS 'qty',
				sf.uom AS 'uom',
				SUM(sfm.last_year_forecast_qty) AS 'last_year_forecast_qty',
				SUM(sfm.last_year_actual_qty) AS 'last_year_actual_qty',
				sf.company AS 'company',
				sf.business_unit AS 'business_unit'
			FROM `tabSales Forecast Month` AS `sfm`
			LEFT JOIN `tabSales Forecast` AS `sf` ON sf.name = sfm.parent
			{}
			GROUP BY sfm.month, sf.item_code
			ORDER BY sf.item_code, sfm.idx
		""".format(get_conditions(filters)),
		filters
	)

def get_conditions(filters):
	conditions = """
		WHERE sf.company = %(company)s
		AND sf.business_unit = %(business_unit)s
	"""

	if filters.get('item_code'):
		conditions += "AND sf.item_code = %(item_code)s"

	return conditions
