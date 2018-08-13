# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.report.financial_statements import filter_accounts, filter_out_zero_value_rows

def execute(filters=None):
	accounts = get_accounts_data(filters.get("company"))
	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
	data = get_data(accounts, parent_children_map)
	columns = get_columns(filters)
	return columns, data

def get_accounts_data(company):
	return frappe.db.sql("""select name, name as account, parent_account, account_name, lft, rgt, root_type, account_type, account_currency
		from `tabAccount` where company=%s order by name""", company, as_dict=True)

def get_data(accounts, parent_children_map):
	data = []

	for d in accounts:
		row = {
			"account_name": d.account_name or d.name,
			"account": d.name,
			"parent_account": d.parent_account,
			"indent": d.indent,
			"account_currency": d.account_currency,
			"root_type": d.root_type, 
			"account_type": d.account_type
		}
		data.append(row)

	return data

def get_columns(filters):
	return [
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 300
		},
		{
			"fieldname": "root_type",
			"label": _("Root Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "account_type",
			"label": _("Account Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "account_currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"width": 100
		}
	]

