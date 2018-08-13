# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	report = SalesPersonSalesSummaryReport(filters)
	return report.get_columns(), report.get_data()

class SalesPersonSalesSummaryReport(object):
	def __init__(self, filters):
		self.filters = filters
		self.set_columns()
		self.set_data()

	def get_columns(self):
		return self.columns

	def get_data(self):
		return self.data

	def set_columns(self):
		self.columns = [
			{
				'label': _('Sales Person'),
				'fieldname': 'sales_person',
				'fieldtype': 'Link',
				'options': 'Sales Person',
				'width': 160
			},
			{
				'label': _('Qty'),
				'fieldname': 'qty',
				'fieldtype': 'Float',
				'width': 120
			},
			{
				'label': _('Rate'),
				'fieldname': 'rate',
				'fieldtype': 'Currency',
				'width': 120
			}
		]

	def set_data(self):
		self.data = []

		for sales_person in self.get_sales_persons():
			totals = self.get_totals(sales_person)

			self.data.append({
				'sales_person': sales_person.name,
				'qty': totals.qty,
				'rate': totals.rate
			})

	def get_sales_persons(self):
		return frappe.db.sql(
			"""
				SELECT sp.name
				FROM `tabSales Person` AS `sp`
				ORDER BY sp.name
			""",
			self.filters,
			as_dict=True
		)

	def get_totals(self, sales_person):
		totals = frappe.db.sql(
			"""
				SELECT
					IFNULL(SUM(sii.qty), 0.0) AS 'qty',
					IFNULL(SUM(sii.rate), 0.0) AS 'rate'
				FROM `tabSales Team` AS `st`
				LEFT JOIN `tabSales Invoice` AS `si`
					ON si.name = st.parent
					AND 1 = 1
				LEFT JOIN `tabSales Invoice Item` AS `sii` ON sii.parent = si.name
				WHERE st.sales_person = '{sales_person}'
				GROUP BY st.sales_person
			""".format(sales_person=sales_person.name),
			self.filters,
			as_dict=True
		)

		if not totals:
			totals = [frappe._dict({'qty': 0.0, 'rate': 0.0})]

		return totals[0]
