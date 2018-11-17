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
		self.set_conditions()
		self.set_columns()
		self.set_data()
		self.add_total_row()

	def set_conditions(self):
		self.conditions = "WHERE si.docstatus = 1"

		if self.filters.get("from_date") and self.filters.get("to_date"):
			self.conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"

		if self.filters.get("from_date") and not self.filters.get("to_date"):
			self.conditions += " AND si.posting_date >= %(from_date)s"

		if not self.filters.get("from_date") and self.filters.get("to_date"):
			self.conditions += " AND si.posting_date <= %(to_date)s"

	def set_columns(self):
		self.columns = [
			{
				"label": _("Sales Person"),
				"fieldname": "sales_person",
				"fieldtype": "Link",
				"options": "Sales Person",
				"width": 160
			},
			{
				"label": _("Customer"),
				"fieldname": "customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 160
			},
			{
				"label": _("Customer Name"),
				"fieldname": "customer_name",
				"fieldtype": "Data",
				"width": 160
			},
			{
				"label": _("Customer Group"),
				"fieldname": "customer_group",
				"fieldtype": "Link",
				"options": "Customer Group",
				"width": 120
			},
			{
				"label": _("Territory"),
				"fieldname": "territory",
				"fieldtype": "Link",
				"options": "Territory",
				"width": 120
			},
			{
				"label": _("Qty"),
				"fieldname": "qty",
				"fieldtype": "Float",
				"width": 120
			},
			{
				"label": _("Rate"),
				"fieldname": "rate",
				"fieldtype": "Currency",
				"width": 120
			}
		]

	def set_data(self):
		self.data = frappe.db.sql(
			"""
				SELECT
					st.sales_person,
					si.customer,
					c.customer_name,
					c.customer_group,
					c.territory,
					IFNULL(SUM(sii.stock_qty), 0.0) AS 'qty',
					IFNULL(SUM(sii.base_rate), 0.0) AS 'rate'
				FROM `tabSales Invoice` AS `si`
				LEFT JOIN `tabSales Invoice Item` AS `sii` ON sii.parent = si.name
				LEFT JOIN `tabSales Team` AS `st` ON st.parent = si.name
				LEFT JOIN `tabCustomer` AS `c` ON c.name = si.customer
				{conditions}
				GROUP BY st.sales_person, si.customer
				ORDER BY st.sales_person, si.customer
			""".format(conditions = self.conditions),
			self.filters,
			as_dict=True
		)

	def add_total_row(self):
		if len(self.data) < 2: return

		total_row = frappe._dict({
			"sales_person": "'Total'",
			"qty": 0.0,
			"rate": 0.0
		})

		for row in self.data:
			total_row.qty += row.qty
			total_row.rate += row.rate

		self.data.append(total_row)
