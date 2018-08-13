# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	return [
		_('Year') + ':Int:',
		_('Month') + '::',
		_('Sales Person') + ':Link/Sales Person:120',
		_('Customer') + ':Link/Customer:120',
		_('Customer Name') + '::160',
		_('Item') + ':Link/Item:120',
		_('Item Name') + '::160',
		_('Qty') + ':Float:',
		_('Rate') + ':Currency:',
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
				sf.year,
				sfm.month,
				sf.sales_person,
				sf.customer,
				sf.customer_name,
				sf.item_code,
				sf.item_name,
				sfm.qty,
				sfm.rate,
				sf.uom,
				sfm.last_year_forecast_qty,
				sfm.last_year_actual_qty,
				sf.company,
				sf.business_unit
			FROM `tabSales Forecast Month` AS `sfm`
			LEFT JOIN `tabSales Forecast` AS `sf` ON sf.name = sfm.parent
			{}
			ORDER BY sf.year, sfm.idx, sf.sales_person, sf.customer, sf.item_code
		""".format(get_conditions(filters)),
		filters
	)

def get_conditions(filters):
	conditions = """
		WHERE sf.company = %(company)s
		AND sf.business_unit = %(business_unit)s
	"""

	if filters.get('item_code'):
		conditions += " AND sf.item_code = %(item_code)s"

	if filters.get('customer'):
		conditions += " AND sf.customer = %(customer)s"

	if filters.get('sales_person'):
		conditions += " AND sf.sales_person = %(sales_person)s"

	if filters.get('year'):
		conditions += " AND sf.year = %(year)s"

	if filters.get('month'):
		conditions += " AND sfm.idx = %(month)s"

	return conditions
