# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import datetime
import json

import six

import frappe
from frappe import _
from frappe.desk.reportview import get_match_cond, get_filters_cond

from erpnext.selling.sales_forecast_common import SalesForecastCommon

class SalesForecast(SalesForecastCommon):
	def validate(self):
		self.validate_year()
		self.validate_period_existence()
		self.validate_sales_person()
		self.validate_business_unit()
		self.validate_uniqueness(self.get_filters())

	def validate_period_existence(self):
		if not frappe.db.get_value('Sales Forecast Period', {'year': self.year}):
			frappe.throw(_('{} is not open for {}'.format(self.doctype, self.year)))

	def validate_sales_person(self):
		if self.sales_person != get_sales_person():
			frappe.throw('Invalid Sales Person')

	def validate_business_unit(self):
		business_unit_company = frappe.db.get_value('Business Unit', self.business_unit, 'company')

		if (self.company != business_unit_company):
			frappe.throw(_('{} is not affiliated to {} company').format(self.business_unit, self.company))

	def get_filters(self):
		filters = get_conditions(self)
		filters['name'] = ['!=', self.name]
		filters['year'] = self.year
		return filters

@frappe.whitelist()
def get_sales_person():
	employee = frappe.db.get_value('Employee', {'user_id': frappe.session.user, 'status': 'Active'})

	if employee:
		return frappe.db.get_value('Sales Person', {'employee': employee, 'enabled': 1})

# Override erpnext.controllers.queries.customer_query
@frappe.whitelist()
def customer_query(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	cust_master_name = frappe.defaults.get_user_default("cust_master_name")

	if cust_master_name == "Customer Name":
		fields = ["c.name", "c.customer_group", "c.territory"]
	else:
		fields = ["c.name", "c.customer_name", "c.customer_group", "c.territory"]

	meta = frappe.get_meta("Customer")
	searchfields = meta.get_search_fields()
	searchfields = searchfields + [f for f in [searchfield or "name", "customer_name"] \
			if not f in searchfields]
	searchfields = ["c." + f for f in searchfields]
	fields = fields + [f for f in searchfields if not f in fields]

	fields = ", ".join(fields)
	searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])

	return frappe.db.sql("""select {fields} from `tabSales Team` as `st`
		left join `tabCustomer` as `c` on c.name = st.parent
		where st.sales_person = '{sales_person}'
			and c.docstatus < 2
			and ({scond}) and c.disabled=0
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, c.name), locate(%(_txt)s, c.name), 99999),
			if(locate(%(_txt)s, c.customer_name), locate(%(_txt)s, c.customer_name), 99999),
			c.idx desc,
			c.name, c.customer_name
		limit %(start)s, %(page_len)s""".format(**{
			"fields": fields,
			"scond": searchfields,
			"mcond": get_match_cond(doctype),
			"fcond": get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
			"sales_person": get_sales_person()
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})

@frappe.whitelist()
def get_items(doc):
	if isinstance(doc, six.string_types):
		doc = frappe.get_doc(json.loads(doc))

	last_forecast = get_last_forecast(doc)
	items = []

	if not last_forecast:
		return

	for last_item in last_forecast.get('items'):
		item = get_item_data(last_item, doc)
		items.append(item)

	return items

@frappe.whitelist()
def get_last_forecast(doc):
	if isinstance(doc, six.string_types):
		doc = frappe.get_doc(json.loads(doc))

	last_forecast = frappe.get_value(doc.doctype, get_conditions(doc))

	if last_forecast:
		return frappe.get_doc(doc.doctype, last_forecast)

@frappe.whitelist()
def get_item(item, doc):
	if isinstance(doc, six.string_types):
		doc = frappe.get_doc(json.loads(doc))

	if isinstance(item, six.string_types):
		item = frappe.get_doc(json.loads(item))

	last_item = get_last_year_item(item, doc)

	if not last_item:
		last_item = item

	return get_item_data(last_item, doc)

@frappe.whitelist()
def get_item_price_and_rate(item, doc):
	if isinstance(doc, six.string_types):
		doc = frappe.get_doc(json.loads(doc))

	if isinstance(item, six.string_types):
		item = frappe.get_doc(json.loads(item))

	conditions = get_conditions(doc)
	conditions['item_code'] = item.item

	data = frappe.db.sql(
		"""
			SELECT sii.base_price_list_rate, sii.base_rate
			FROM `tabSales Invoice` AS `si`
			LEFT JOIN `tabSales Invoice Item` AS `sii` ON sii.parent = si.name
			WHERE si.docstatus = 1
			AND si.is_return = 0
			AND si.company = %(company)s
			AND si.business_unit = %(business_unit)s
			AND sii.item_code = %(item_code)s
			ORDER BY si.posting_date DESC, si.posting_time DESC
			LIMIT 1
		""",
		conditions,
		as_dict=True
	)

	if data:
		return data[0]

@frappe.whitelist()
def get_month_statuses(doc):
	if isinstance(doc, six.string_types):
		doc = frappe._dict(json.loads(doc))

	statuses = []
	end_dates = get_end_dates(doc, True) or get_end_dates(doc)

	if not end_dates:
		frappe.throw(_('Sales Forecast Period is not found'))

	for i in range(0, 12):
		statuses.append(datetime.date.today() <= end_dates[i // 3])

	return statuses

def get_conditions(doc):
	return {
		'company': doc.company,
		'business_unit': doc.business_unit,
		'year': doc.year - 1,
		'customer': doc.customer
	}

def get_item_data(last_item, doc):
	actual_qtys = get_last_year_actual_qtys(doc, last_item)

	return {
		'item': last_item.item,
		'item_name': last_item.item_name,
		'last_year_forecast_qty_q11': last_item.qty_q11,
		'last_year_forecast_qty_q12': last_item.qty_q12,
		'last_year_forecast_qty_q13': last_item.qty_q13,
		'last_year_forecast_qty_q24': last_item.qty_q24,
		'last_year_forecast_qty_q25': last_item.qty_q25,
		'last_year_forecast_qty_q26': last_item.qty_q26,
		'last_year_forecast_qty_q37': last_item.qty_q37,
		'last_year_forecast_qty_q38': last_item.qty_q38,
		'last_year_forecast_qty_q39': last_item.qty_q39,
		'last_year_forecast_qty_q410': last_item.qty_q410,
		'last_year_forecast_qty_q411': last_item.qty_q411,
		'last_year_forecast_qty_q412': last_item.qty_q412,
		'last_year_actual_qty_q11': actual_qtys[0].stock_qty,
		'last_year_actual_qty_q12': actual_qtys[1].stock_qty,
		'last_year_actual_qty_q13': actual_qtys[2].stock_qty,
		'last_year_actual_qty_q24': actual_qtys[3].stock_qty,
		'last_year_actual_qty_q25': actual_qtys[4].stock_qty,
		'last_year_actual_qty_q26': actual_qtys[5].stock_qty,
		'last_year_actual_qty_q37': actual_qtys[6].stock_qty,
		'last_year_actual_qty_q38': actual_qtys[7].stock_qty,
		'last_year_actual_qty_q39': actual_qtys[8].stock_qty,
		'last_year_actual_qty_q410': actual_qtys[9].stock_qty,
		'last_year_actual_qty_q411': actual_qtys[10].stock_qty,
		'last_year_actual_qty_q412': actual_qtys[11].stock_qty
	}

def get_last_year_item(item, doc):
	conditions = get_conditions(doc)
	conditions['item'] = item.item

	items = frappe.db.sql(
		"""
			SELECT sfi.*
			FROM `tabSales Forecast` AS `sf`
			LEFT JOIN `tabSales Forecast Item` AS `sfi` ON sfi.parent = sf.name
			WHERE sf.company = %(company)s
			AND sf.business_unit = %(business_unit)s
			AND sf.year = %(year)s
			AND sf.customer = %(customer)s
			AND sfi.item = %(item)s
			ORDER BY sfi.creation DESC
			LIMIT 1
		""",
		conditions,
		as_dict=True
	)

	if items:
		return items[0]

def get_last_year_actual_qtys(doc, item):
	conditions = get_conditions(doc)
	conditions['item_code'] = item.item

	return frappe.db.sql(
		"""
			SELECT * FROM (
				SELECT
					MONTH(si.posting_date) AS 'month',
					SUM(sii.stock_qty) AS 'stock_qty'
				FROM `tabSales Invoice` AS `si`
				LEFT JOIN `tabSales Invoice Item` AS `sii` ON sii.parent = si.name
				WHERE si.docstatus = 1
				AND si.company = %(company)s
				AND si.business_unit = %(business_unit)s
				AND YEAR(si.posting_date) = %(year)s
				AND si.customer = %(customer)s
				AND sii.item_code = %(item_code)s
				GROUP BY month
				UNION
				SELECT
					seq AS 'month',
					0.0 AS 'stock_qty'
				FROM seq_1_to_12
			) AS `q`
			GROUP BY q.month
			ORDER BY q.month
		""",
		conditions,
		as_dict=True
	)

def get_end_dates(doc, by_sales_person=False):
	end_dates = frappe.db.sql(
		"""
			SELECT q1_end_date, q2_end_date, q3_end_date, q4_end_date
			FROM `tabSales Forecast Period`
			WHERE year = %(year)s
			{}
			ORDER BY modified DESC
		""".format('AND sales_person IS NULL' if not by_sales_person else 'AND sales_person = %(sales_person)s'),
		{'year': doc.year, 'sales_person': doc.sales_person}
	)

	return [date for v in end_dates for date in v]
