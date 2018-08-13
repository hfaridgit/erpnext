# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.selling.doctype.customer.customer import get_customer_outstanding, get_credit_limit

def execute(filters=None):
	if not filters: filters = {}
	#Check if customer id is according to naming series or customer name
	customer_naming_type = frappe.db.get_value("Selling Settings", None, "cust_master_name")
	columns = get_columns(customer_naming_type)

	data = []

	customer_list = get_details(filters)

	for d in customer_list:
		row = []

		outstanding_amt = get_customer_outstanding(d.name, filters.get("company"),
			ignore_outstanding_sales_order=d.bypass_credit_limit_check_at_sales_order)

		credit_limit = get_credit_limit(d.name, filters.get("company"))		

		bal = flt(credit_limit) - flt(outstanding_amt)
		
		credit_days_limit = frappe.get_value("Payment Term", d.payment_terms, "credit_days")
		
		cd = frappe.db.sql("""select datediff(now(), min(due_date)) as credit_days from `tabSales Invoice`
								where outstanding_amount>0 and customer=%s""", (d.name), as_dict=1)
								
		if cd:
			actual_credit_days = cd[0].credit_days
		else:
			actual_credit_days = 0
			
		if customer_naming_type == "Naming Series":
			row = [d.name, d.customer_name, credit_limit, credit_days_limit, outstanding_amt, actual_credit_days, bal,
				d.bypass_credit_limit_check_at_sales_order]
		else:
			row = [d.name, credit_limit, credit_days_limit, outstanding_amt, actual_credit_days, bal, d.bypass_credit_limit_check_at_sales_order]

		if credit_limit:
			data.append(row)

	return columns, data

def get_columns(customer_naming_type):
	columns = [
		_("Customer") + ":Link/Customer:120",
		_("Credit Limit") + ":Currency:120",
		_("Days Limit") + ":Currency:120",
		_("Outstanding Amt") + ":Currency:100",
		_("Actual Days") + ":Currency:120",
		_("Credit Balance") + ":Currency:120",
		_("Bypass credit check at Sales Order ") + ":Check:120"
	]

	if customer_naming_type == "Naming Series":
		columns.insert(1, _("Customer Name") + ":Data:120")

	return columns

def get_details(filters):
	conditions = ""

	if filters.get("customer"):
		conditions += " where name = %(customer)s"

	return frappe.db.sql("""select name, customer_name, payment_terms, 
		bypass_credit_limit_check_at_sales_order from `tabCustomer` %s
	""" % conditions, filters, as_dict=1)