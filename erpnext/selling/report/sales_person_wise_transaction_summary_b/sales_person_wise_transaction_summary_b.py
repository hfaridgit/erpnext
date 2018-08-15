# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters = {}

	# @custom
	filters.doc_type = "Sales Invoice"

	columns = get_columns(filters)
	entries = get_entries(filters)
	item_details = get_item_details()

	# @custom
	customer_details = get_customer_details()

	data = []

	# @custom
	for d in entries:
		forecast_qty = get_forecast_qty(filters, d)
		qty_percentage = (d.stock_qty / forecast_qty) * 100 if forecast_qty > 0.0 else 0.0

		data.append([
			d.name, d.customer,
			customer_details.get(d.customer, {}).get("customer_name"),
			customer_details.get(d.customer, {}).get("customer_group"), d.territory,
			customer_details.get(d.customer, {}).get("credit_limit"),
			customer_details.get(d.customer, {}).get("payment_terms"),
			d.posting_date, d.due_date, d.item_code,
			item_details.get(d.item_code, {}).get("item_name"), item_details.get(d.item_code, {}).get("item_group"), item_details.get(d.item_code, {}).get("brand"),
			d.qty, d.stock_qty, forecast_qty, qty_percentage,
			d.base_net_amount, d.sales_person, d.allocated_percentage, d.contribution_amt
		])

	if data:
		total_row = [""]*len(data[0])
		data.append(total_row)

	return columns, data

def get_columns(filters):
	if not filters.get("doc_type"):
		msgprint(_("Please select the document type first"), raise_exception=1)

	# @custom
	return [filters["doc_type"] + ":Link/" + filters["doc_type"] + ":140",
		_("Customer Code") + ":Link/Customer:140", _("Customer Name") + "::120",
		_("Customer Group") + ":Link/Customer Group:100",
		_("Territory") + ":Link/Territory:100", _("Credit Limit") + ":Currency:100",
		_("Default Payment Terms Template") + ":Link/Payment Terms Template:100",
		_("Posting Date") + ":Date:100", _("Due Date") + ":Date:100",
		_("Item Code") + ":Link/Item:120", _("Item Name") + "::120",
		_("Item Group") + ":Link/Item Group:120", _("Brand") + ":Link/Brand:120",
		_("Qty") + ":Float:100", _("Stock Qty") + ":Float:100", _("Forecast Qty") + ":Float:100",
		_("Qty %") + ":Percent:100", _("Amount") + ":Currency:120",
		_("Sales Person") + ":Link/Sales Person:140", _("Contribution %") + "::110",
		_("Contribution Amount") + ":Currency:140"]

def get_entries(filters):
	date_field = filters["doc_type"] == "Sales Order" and "transaction_date" or "posting_date"
	conditions, values = get_conditions(filters, date_field)

	# @custom
	entries = frappe.db.sql("""
		select
			dt.name, dt.customer, dt.territory, dt.%s as posting_date, dt.due_date, dt_item.item_code,
			dt_item.qty, dt_item.stock_qty, dt_item.base_net_amount, st.sales_person, st.allocated_percentage,
			dt_item.base_net_amount*st.allocated_percentage/100 as contribution_amt
		from
			`tab%s` dt, `tab%s Item` dt_item, `tabSales Team` st
		where
			st.parent = dt.name and dt.name = dt_item.parent and st.parenttype = %s
			and dt.docstatus = 1 %s order by st.sales_person, dt.name desc
		""" %(date_field, filters["doc_type"], filters["doc_type"], '%s', conditions),
			tuple([filters["doc_type"]] + values), as_dict=1)

	return entries

def get_conditions(filters, date_field):
	conditions = [""]
	values = []

	# @custom
	for field in ["company", "business_unit", "customer", "territory"]:
		if filters.get(field):
			conditions.append("dt.{0}=%s".format(field))
			values.append(filters[field])

	if filters.get("sales_person"):
		lft, rgt = frappe.get_value("Sales Person", filters.get("sales_person"), ["lft", "rgt"])
		conditions.append("exists(select name from `tabSales Person` where lft >= {0} and rgt <= {1} and name=st.sales_person)".format(lft, rgt))

	if filters.get("from_date"):
		conditions.append("dt.{0}>=%s".format(date_field))
		values.append(filters["from_date"])

	if filters.get("to_date"):
		conditions.append("dt.{0}<=%s".format(date_field))
		values.append(filters["to_date"])

	items = get_items(filters)
	if items:
		conditions.append("dt_item.item_code in (%s)" % ', '.join(['%s']*len(items)))
		values += items

	# @custom
	if filters.get("item_code"):
		conditions.append("dt_item.item_code = %s")
		values.append(filters["item_code"])

	# @custom
	if filters.get("overdue"):
		conditions.append("dt.status = 'Overdue'")

	return " and ".join(conditions), values

def get_items(filters):
	if filters.get("item_group"): key = "item_group"
	elif filters.get("brand"): key = "brand"
	else: key = ""

	items = []
	if key:
		items = frappe.db.sql_list("""select name from tabItem where %s = %s""" %
			(key, '%s'), (filters[key]))

	return items

def get_item_details():
	item_details = {}

	# @custom
	for d in frappe.db.sql("""select name, item_name, item_group, brand from `tabItem`""", as_dict=1):
		item_details.setdefault(d.name, d)

	return item_details

# @custom
def get_customer_details():
	customer_details = {}

	for d in frappe.db.sql("""select name, customer_name, customer_group, credit_limit, payment_terms from `tabCustomer`""", as_dict=1):
		customer_details.setdefault(d.name, d)

	return customer_details

# @custom
def get_forecast_qty(filters, row):
	qty_fields = ["qty_q11", "qty_q12", "qty_q13", "qty_q24", "qty_q25", "qty_q26", "qty_q37", "qty_q38", "qty_q39", "qty_q410", "qty_q411", "qty_q412"]
	conditions = "where sf.company = %(company)s"

	if filters.get("business_unit"):
		conditions += " and sf.business_unit = %(business_unit)s"

	conditions += " and sf.year = {}".format(row.posting_date.year)
	conditions += " and sf.customer = '{}'".format(row.customer)
	conditions += " and sfi.item = '{}'".format(row.item_code)

	forecast = frappe.db.sql("""
		select {select_field} qty from `tabSales Forecast` sf
		left join `tabSales Forecast Item` sfi on sfi.parent = sf.name
		{conditions}
	""".format(select_field = qty_fields[row.posting_date.month - 1], conditions = conditions),
	filters, as_dict=1)

	return forecast[0].qty if forecast else 0.0
