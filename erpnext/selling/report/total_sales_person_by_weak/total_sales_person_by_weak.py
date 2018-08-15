# -*- coding: utf-8 -*-
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	report = Report(filters)
	return report.columns, report.data

class Report(object):
	def __init__(self, filters):
		self.filters = filters
		self.validate_filters()
		self.set_columns()
		self.set_data()

	def validate_filters(self):
		if not self.filters.get("year"):
			frappe.throw("'Year is required'")

	def set_columns(self):
		self.columns = [
			{
				"label": _("Week"),
				"fieldname": "week",
				"fieldtype": "Int",
				"width": 60
			},
			{
				"label": _("Sales Person"),
				"fieldname": "sales_person",
				"fieldtype": "Link",
				"options": "Sales Person",
				"width": 160
			},
			{
				"label": _("Total"),
				"fieldname": "total",
				"fieldtype": "Currency",
				"width": 120
			},
			{
				"label": _("Average"),
				"fieldname": "average",
				"fieldtype": "Currency",
				"width": 120
			},
			{
				"label": _("Comulative Total"),
				"fieldname": "comulative_total",
				"fieldtype": "Currency",
				"width": 120
			},
			{
				"label": _("Sales %"),
				"fieldname": "sales",
				"fieldtype": "Percent",
				"width": 120
			}
		]

	def set_data(self):
		self.data = frappe.db.sql(
			"""
				SELECT
					WEEK(si.posting_date, 3) AS 'week',
					st.sales_person,
					SUM(base_total) AS 'total'
				FROM `tabSales Invoice` AS `si`
				LEFT JOIN `tabSales Team` AS `st`
					ON st.parent = si.name
					AND st.idx = 1
				WHERE si.docstatus = 1
				AND st.sales_person IS NOT NULL
				AND YEAR(si.posting_date) = %(year)s
				GROUP BY week, st.sales_person
				ORDER BY week, st.sales_person
			""",
			self.filters,
			as_dict=True
		)

		for week in self.data:
			week.average = week.total / week.week
			week.comulative_total = week.total

		self.set_comulative_total()

	def set_comulative_total(self):
		for i, week in enumerate(self.data):
			if i != 0 and week.sales_person == self.data[i - 1].sales_person:
				week.comulative_total += self.data[i - 1].total
