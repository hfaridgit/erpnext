# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters = {}
	#Check if supplier id is according to naming series or supplier name
	supplier_naming_type = frappe.db.get_value("Buying Settings", None, "supp_master_name")
	columns = get_columns(supplier_naming_type)

	data = []

	supplier_list = get_details(filters)

	for d in supplier_list:
		row = []

		outstanding_amt = get_supplier_outstanding(d.name, filters.get("company"), filters.get("business_unit"))

		credit_limit = get_credit_limit(d.name, filters.get("company"))		

		bal = flt(credit_limit) - flt(outstanding_amt)

		if supplier_naming_type == "Naming Series":
			row = [d.name, d.supplier_name, credit_limit, outstanding_amt, bal]
		else:
			row = [d.name, credit_limit, outstanding_amt, bal]

		if credit_limit:
			data.append(row)

	return columns, data

def get_columns(supplier_naming_type):
	columns = [
		_("Supplier") + ":Link/Supplier:120",
		_("Credit Limit") + ":Currency:120",
		_("Outstanding Amt") + ":Currency:100",
		_("Credit Balance") + ":Currency:120"
	]

	if supplier_naming_type == "Naming Series":
		columns.insert(1, _("Supplier Name") + ":Data:120")

	return columns

def get_details(filters):
	conditions = ""

	if filters.get("supplier"):
		conditions += " where name = %(supplier)s"

	return frappe.db.sql("""select name, supplier_name
		from `tabSupplier` %s
	""" % conditions, filters, as_dict=1)

def get_supplier_outstanding(supplier, company, business_unit, ignore_outstanding_purchase_order=False):
	# Outstanding based on GL Entries
	outstanding_based_on_gle = frappe.db.sql("""
		select sum(debit) - sum(credit)
		from `tabGL Entry`
		where party_type = 'supplier' and party = %s and company=%s and business_unit=%s""", (supplier, company, business_unit))

	outstanding_based_on_gle = flt(outstanding_based_on_gle[0][0]) if outstanding_based_on_gle else 0

	# Outstanding based on Purchase Order
	outstanding_based_on_po = 0.0

	# if credit limit check is bypassed at purchase order level,
	# we should not consider outstanding Purchase Orders, when supplier credit balance report is run
	if not ignore_outstanding_purchase_order:
		outstanding_based_on_po = frappe.db.sql("""
			select sum(base_grand_total*(100 - per_billed)/100)
			from `tabPurchase Order`
			where supplier=%s and docstatus = 1 and company=%s and business_unit=%s
			and per_billed < 100 and status != 'Closed'""", (supplier, company, business_unit))

		outstanding_based_on_po = flt(outstanding_based_on_po[0][0]) if outstanding_based_on_po else 0.0

	# Outstanding based on Purchase Receipt, which are not created against Purchase Order
	unmarked_purchase_receipt_items = frappe.db.sql("""select
			pr_item.name, pr_item.amount, pr.base_net_total, pr.base_grand_total
		from `tabPurchase Receipt` pr, `tabPurchase Receipt Item` pr_item
		where
			pr.name = pr_item.parent
			and pr.supplier=%s and pr.company=%s and pr.business_unit=%s
			and pr.docstatus = 1 and pr.status not in ('Closed', 'Stopped')
			and ifnull(pr_item.purchase_order, '') = ''
		""", (supplier, company, business_unit), as_dict=True)

	outstanding_based_on_pr = 0.0

	for pr_item in unmarked_purchase_receipt_items:
		pi_amount = frappe.db.sql("""select sum(amount)
			from `tabPurchase Invoice Item`
			where pr_detail = %s and docstatus = 1""", pr_item.name)[0][0]

		if flt(pr_item.amount) > flt(pi_amount) and pr_item.base_net_total:
			outstanding_based_on_pr += ((flt(pr_item.amount) - flt(pi_amount)) \
				/ pr_item.base_net_total) * pr_item.base_grand_total

	return outstanding_based_on_gle + outstanding_based_on_po + outstanding_based_on_pr

def get_credit_limit(supplier, company):
	credit_limit = None

	if supplier:
		credit_limit, supplier_type = frappe.db.get_value("Supplier",
			supplier, ["supplier_credit_limit", "supplier_type"])

	if not credit_limit:
		credit_limit = frappe.db.get_value("Company", company, "credit_limit")

	return flt(credit_limit)
