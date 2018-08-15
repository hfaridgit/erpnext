# -*- coding: utf-8 -*-
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from datetime import date, datetime
import frappe
from frappe import _

def execute(filters=None):
	report = Report(filters)
	return report.get_columns(), report.get_data()

class Report(object):
	def __init__(self, filters):
		self.filters = filters
		self.validate_filters()
		self.period = Period(filters).get_period()
		self.set_columns()
		self.set_data()

	def get_columns(self):
		return self.columns

	def get_data(self):
		return self.data

	def validate_filters(self):
		if not self.filters.get("company"):
			frappe.throw(_("'Company' is required"))
		if not self.filters.get("business_unit"):
			frappe.throw(_("'Business Unit' is required"))
		if not self.filters.get("year"):
			frappe.throw(_("'Year' is required"))
		if self.filters.get("period") not in ("Monthly", "Quarterly", "Half-Yearly", "Yearly"):
			frappe.throw(_("'Period' is invalid"))

	def set_columns(self):
		self.columns = [
			{
				"label": _("Sales Forecast"),
				"fieldname": "sales_forecast",
				"fieldtype": "Link",
				"options": "Sales Forecast",
				"width": 120
			},
			{
				"label": _("Sales Person"),
				"fieldname": "sales_person",
				"fieldtype": "Link",
				"options": "Sales Person",
				"width": 120
			},
			{
				"label": _("Customer Code"),
				"fieldname": "customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 120
			},
			{
				"label": _("Customer Name"),
				"fieldname": "customer_name",
				"fieldtype": "Data",
				"width": 120
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
				"label": _("Credit Limits"),
				"fieldname": "credit_limits",
				"fieldtype": "Currency",
				"width": 120
			},
			{
				"label": _("Default Payment Terms Template"),
				"fieldname": "payment_terms",
				"fieldtype": "Link",
				"options": "Payment Terms Template",
				"width": 120
			},
			{
				"label": _("Item Code"),
				"fieldname": "item",
				"fieldtype": "Link",
				"options": "Item",
				"width": 120
			},
			{
				"label": _("Item Name"),
				"fieldname": "item_name",
				"fieldtype": "Data",
				"width": 160
			}
		]

		for i, start_month in enumerate(self.period.start_months):
			self.columns += [
				{
					"label": self.period.labels[i] + " ({})".format("Amt"),
					"fieldname": self.period.field_names[i].amount,
					"fieldtype": "Currency",
					"width": 120
				},
				{
					"label": self.period.labels[i] + " ({})".format("Qty"),
					"fieldname": self.period.field_names[i].qty,
					"fieldtype": "Float",
					"width": 120
				},
				{
					"label": self.period.labels[i] + " ({})".format("Act. Amt"),
					"fieldname": self.period.field_names[i].actual_amount,
					"fieldtype": "Currency",
					"width": 120
				},
				{
					"label": self.period.labels[i] + " ({})".format("Act. Qty"),
					"fieldname": self.period.field_names[i].actual_qty,
					"fieldtype": "Float",
					"width": 120
				}
			]

	def set_data(self):
		self.data = frappe.db.sql(
			"""
				SELECT
					sf.name AS 'sales_forecast',
					sf.sales_person,
					sf.customer,
					c.customer_name,
					c.customer_group,
					c.territory,
					c.credit_limit,
					c.payment_terms,
					sfi.item,
					i.item_name,
					{select_columns}
				FROM `tabSales Forecast` AS `sf`
				LEFT JOIN `tabSales Forecast Item` AS `sfi` ON sfi.parent = sf.name
				LEFT JOIN `tabItem` AS `i` ON i.name = sfi.item
				LEFT JOIN `tabCustomer` AS `c` ON c.name = sf.customer
				WHERE sf.company = %(company)s
				AND sf.business_unit = %(business_unit)s
				AND sf.year = %(year)s
				ORDER BY sf.name, sfi.item
			""".format(
				select_columns = self.get_select_columns()
			),
			self.filters,
			as_dict=True
		)

		self.set_actuals()
		self.add_total_row()

	def get_select_columns(self):
		if self.filters.period == "Monthly":
			select_columns = """
				sfi.qty_q11 * sfi.final_price_q11 AS 'amount01',
				sfi.qty_q11 AS 'qty01',
				sfi.qty_q12 * sfi.final_price_q12 AS 'amount02',
				sfi.qty_q12 AS 'qty02',
				sfi.qty_q13 * sfi.final_price_q13 AS 'amount03',
				sfi.qty_q13 AS 'qty03',
				sfi.qty_q24 * sfi.final_price_q24 AS 'amount04',
				sfi.qty_q24 AS 'qty04',
				sfi.qty_q25 * sfi.final_price_q25 AS 'amount05',
				sfi.qty_q25 AS 'qty05',
				sfi.qty_q26 * sfi.final_price_q26 AS 'amount06',
				sfi.qty_q26 AS 'qty06',
				sfi.qty_q37 * sfi.final_price_q37 AS 'amount07',
				sfi.qty_q37 AS 'qty07',
				sfi.qty_q38 * sfi.final_price_q38 AS 'amount08',
				sfi.qty_q38 AS 'qty08',
				sfi.qty_q39 * sfi.final_price_q39 AS 'amount09',
				sfi.qty_q39 AS 'qty09',
				sfi.qty_q410 * sfi.final_price_q410 AS 'amount10',
				sfi.qty_q410 AS 'qty10',
				sfi.qty_q411 * sfi.final_price_q411 AS 'amount11',
				sfi.qty_q411 AS 'qty11',
				sfi.qty_q412 * sfi.final_price_q412 AS 'amount12',
				sfi.qty_q412 AS 'qty12'
			"""

		if self.filters.period == "Quarterly":
			select_columns = """
				(sfi.qty_q11 + sfi.qty_q12 + sfi.qty_q13)
					* (sfi.final_price_q11 + sfi.final_price_q12 + sfi.final_price_q13)
					AS 'amount01',
				sfi.qty_q11 + sfi.qty_q12 + sfi.qty_q13 AS 'qty01',
				(sfi.qty_q24 + sfi.qty_q25 + sfi.qty_q26)
					* (sfi.final_price_q24 + sfi.final_price_q25 + sfi.final_price_q26)
					AS 'amount02',
				sfi.qty_q24 + sfi.qty_q25 + sfi.qty_q26 AS 'qty02',
				(sfi.qty_q37 + sfi.qty_q38 + sfi.qty_q39)
					* (sfi.final_price_q37 + sfi.final_price_q38 + sfi.final_price_q39)
					AS 'amount03',
				sfi.qty_q37 + sfi.qty_q38 + sfi.qty_q39 AS 'qty03',
				(sfi.qty_q410 + sfi.qty_q411 + sfi.qty_q412)
					* (sfi.final_price_q410 + sfi.final_price_q411 + sfi.final_price_q412)
					AS 'amount04',
				sfi.qty_q410 + sfi.qty_q411 + sfi.qty_q412 AS 'qty04'
			"""

		if self.filters.period == "Half-Yearly":
			select_columns = """
				(sfi.qty_q11 + sfi.qty_q12 + sfi.qty_q13 + sfi.qty_q24 + sfi.qty_q25 + sfi.qty_q26)
					* (sfi.final_price_q11 + sfi.final_price_q12 + sfi.final_price_q13 + sfi.final_price_q24 + sfi.final_price_q25 + sfi.final_price_q26)
					AS 'amount01',
				sfi.qty_q11 + sfi.qty_q12 + sfi.qty_q13 + sfi.qty_q24 + sfi.qty_q25 + sfi.qty_q26 AS 'qty01',
				(sfi.qty_q37 + sfi.qty_q38 + sfi.qty_q39 + sfi.qty_q410 + sfi.qty_q411 + sfi.qty_q412)
					* (sfi.final_price_q37 + sfi.final_price_q38 + sfi.final_price_q39 + sfi.final_price_q410 + sfi.final_price_q411 + sfi.final_price_q412)
					AS 'amount02',
				sfi.qty_q37 + sfi.qty_q38 + sfi.qty_q39 + sfi.qty_q410 + sfi.qty_q411 + sfi.qty_q412 AS 'qty02'
			"""

		if self.filters.period == "Yearly":
			select_columns = """
				(sfi.qty_q11 + sfi.qty_q12 + sfi.qty_q13 + sfi.qty_q24 + sfi.qty_q25 + sfi.qty_q26 + sfi.qty_q37 + sfi.qty_q38 + sfi.qty_q39 + sfi.qty_q410 + sfi.qty_q411 + sfi.qty_q412)
					* (sfi.final_price_q11 + sfi.final_price_q12 + sfi.final_price_q13 + sfi.final_price_q24 + sfi.final_price_q25 + sfi.final_price_q26 + sfi.final_price_q37 + sfi.final_price_q38 + sfi.final_price_q39 + sfi.final_price_q410 + sfi.final_price_q411 + sfi.final_price_q412)
					AS 'amount01',
				sfi.qty_q11 + sfi.qty_q12 + sfi.qty_q13 + sfi.qty_q24 + sfi.qty_q25 + sfi.qty_q26 + sfi.qty_q37 + sfi.qty_q38 + sfi.qty_q39 + sfi.qty_q410 + sfi.qty_q411 + sfi.qty_q412 AS 'qty01'
			"""

		return select_columns

	def set_actuals(self):
		for item in self.data:
			for i, start_month in enumerate(self.period.start_months):
				values = self.filters.copy().update(item)

				actuals = frappe.db.sql(
					"""
						SELECT
							SUM(sii.base_amount) AS 'base_amount',
							SUM(sii.stock_qty) AS 'stock_qty'
						FROM `tabSales Invoice` AS `si`
						LEFT JOIN `tabSales Invoice Item` AS `sii` ON sii.parent = si.name
						WHERE si.docstatus = 1
						AND si.company = %(company)s
						AND si.business_unit = %(business_unit)s
						AND YEAR(si.posting_date) = %(year)s
						AND MONTH(si.posting_date) BETWEEN {start_month} AND {end_month}
						AND si.customer = %(customer)s
						AND sii.item_code = %(item)s
						GROUP BY sii.item_code
					""".format(
						start_month = start_month,
						end_month = start_month + (self.period.step - 1)
					),
					values,
					as_dict=True
				)

				if actuals:
					item[self.period.field_names[i].actual_amount] = actuals[0].base_amount
					item[self.period.field_names[i].actual_qty] = actuals[0].stock_qty
				else:
					item[self.period.field_names[i].actual_amount] = 0.0
					item[self.period.field_names[i].actual_qty] = 0.0

	def add_total_row(self):
		if not self.data: return
		total_row = frappe._dict()

		for i, start_month in enumerate(self.period.start_months):
			total_row.sales_forecast = _("'Total'")
			total_row[self.period.field_names[i].amount] = 0.0
			total_row[self.period.field_names[i].qty] = 0.0
			total_row[self.period.field_names[i].actual_amount] = 0.0
			total_row[self.period.field_names[i].actual_qty] = 0.0

			for item in self.data:
				total_row[self.period.field_names[i].amount] += item[self.period.field_names[i].amount]
				total_row[self.period.field_names[i].qty] += item[self.period.field_names[i].qty]
				total_row[self.period.field_names[i].actual_amount] += item[self.period.field_names[i].actual_amount]
				total_row[self.period.field_names[i].actual_qty] += item[self.period.field_names[i].actual_qty]

		self.data.append(total_row)

class Period(object):
	def __init__(self, filters):
		self.filters = filters
		self.set_period()
		self.set_step()
		self.set_start_months()
		self.set_labels()
		self.set_field_names()

	def get_period(self):
		return self.period

	def set_period(self):
		self.period = frappe._dict({"labels": [], "field_names": []})

	def set_step(self):
		self.period.step = {
			"Monthly": 1,
			"Quarterly": 3,
			"Half-Yearly": 6,
			"Yearly": 12
		}.get(self.filters.period)

	def set_start_months(self):
		self.period.start_months = xrange(1, 13, self.period.step)

	def set_labels(self):
		for i, start_month in enumerate(self.period.start_months):
			if self.period.step == 1:
				label = _(date(1900, start_month, 1).strftime("%b"))
			elif self.period.step == 12:
				label = _(self.filters.get("year"))
			else:
				label = "{}-{}".format(
					_(date(1900, start_month, 1).strftime("%b")),
					_(date(1900, start_month + (self.period.step - 1), 1).strftime("%b"))
				)

			self.period.labels.append(label)

	def set_field_names(self):
		for i, start_month in enumerate(self.period.start_months):
			self.period.field_names.append(frappe._dict({
				"amount": "amount{:02d}".format(i + 1),
				"qty": "qty{:02d}".format(i + 1),
				"actual_amount": "actual_amount{:02d}".format(i + 1),
				"actual_qty": "actual_qty{:02d}".format(i + 1)
			}))
