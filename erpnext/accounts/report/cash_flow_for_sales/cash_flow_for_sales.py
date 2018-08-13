# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	validate_filters(filters)

	return get_columns(filters), get_data(filters)

def validate_filters(filters):
	if not filters.get('company'):
		frappe.throw(_("'Company' is required"))

	if not filters.get('from_date'):
		frappe.throw(_("'From Date' is required"))

	if not filters.get('to_date'):
		frappe.throw(_("'To Date' is required"))

	if filters.from_date > filters.to_date:
		frappe.throw(_("'From Date' must be before 'To Date'"))

def get_columns(filters):
	return [
		_('Sales Invoice') + ':Link/Sales Invoice:120',
		_('Posting Date') + ':Date:100',
		_('Due Date') + ':Date:100',
		_('Item Code') + ':Link/Item:120',
		_('Item Name') + '::120',
		_('Customer Code') + ':Link/Customer:120',
		_('Customer Name') + '::160',
		_('Customer Group') + ':Link/Customer Group:120',
		_('Credit Limit') + ':Currency:100',
		_('Default Payment Terms Template') + ':Link/Payment Terms Template:120',
		_('Sales Person') + ':Link/Sales Person:120',
		_('Total') + ':Currency:100',
		_('Total after Taxes') + ':Currency:100',
		_('Paid') + ':Currency:100',
		_('Returned') + ':Currency:100',
		_('Remained') + ':Currency:100',
		_('Overdue Days') + ':Int:80'
	]

def get_data(filters):
	return frappe.db.sql(
		"""
		SELECT
			sales_invoice,
			posting_date,
			due_date,
			item_code,
			item_name,
			customer,
			customer_name,
			customer_group,
			credit_limit,
			payment_terms,
			sales_person,
			total,
			rounded_total,
			rounded_total - outstanding_amount + IFNULL(returned, 0.0) AS 'paid',
			IFNULL(returned, 0.0) AS 'returned',
			outstanding_amount,
			overdue_days
		FROM (
			SELECT
				si.name AS 'sales_invoice',
				si.posting_date,
				si.due_date,
				sii.item_code,
				sii.item_name,
				si.customer,
				c.customer_name,
				c.customer_group,
				c.credit_limit,
				c.payment_terms,
				st.sales_person,
				si.total,
				si.rounded_total,
				(
					SELECT SUM(si2.total)
					FROM `tabSales Invoice` AS `si2`
					WHERE si2.docstatus = 1
					AND si2.is_return = 1
					AND si2.return_against = si.name
					GROUP BY si2.return_against
				) AS 'returned',
				si.outstanding_amount,
				CURDATE() - si.due_date AS 'overdue_days'
			FROM `tabSales Invoice` AS `si`
			LEFT JOIN `tabSales Invoice Item` AS `sii` ON sii.parent = si.name
			LEFT JOIN `tabSales Team` AS `st` ON st.parent = si.name
			LEFT JOIN `tabCustomer` AS `c` ON c.name = si.customer
			WHERE si.docstatus = 1
			AND si.is_return = 0
			{conditions}
			ORDER BY si.name, sii.item_code
		) AS `cffs`
		""".format(conditions = get_conditions(filters)),
		filters
	)

def get_conditions(filters):
	conditions = ""

	if filters.get('company'):
		conditions += " AND si.company = %(company)s"

	if filters.get('business_unit'):
		conditions += " AND si.business_unit = %(business_unit)s"

	if filters.get('from_date') and filters.get('to_date'):
		conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"

	if filters.get('customer'):
		conditions += " AND si.customer = %(customer)s"

	if filters.get('customer_group'):
		conditions += " AND c.customer_group = %(customer_group)s"

	if filters.get('sales_person'):
		conditions += " AND st.sales_person = %(sales_person)s"

	if filters.get('overdue'):
		conditions += " AND si.status = 'Overdue'"

	return conditions
