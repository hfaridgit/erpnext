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

	if not filters.get('business_unit'):
		frappe.throw(_("'Business Unit' is required"))

	if (filters.get('month_from') or filters.get('month_to')) and not filters.get('year'):
		frappe.throw(_("Please enter a year first"))

	if filters.get('month_from') and filters.get('month_to') and filters.get('month_from') > filters.get('month_to'):
		frappe.throw(_("'From Month' must be less than or equal to 'To Month'"))

def get_columns(filters):
	return [
		_('Year') + ':Int:80',
		_('Month') + ':Int:80',
		_('Customer Code') + ':Link/Customer:120',
		_('Customer Name') + '::160',
		_('Customer Group') + ':Link/Customer Group:120',
		_('Territory') + ':Link/Territory:120',
		_('Credit Limit') + ':Currency:100',
		_('Default Payment Terms Template') + ':Link/Payment Terms Template:120',
		_('Sales Person') + ':Link/Sales Person:120',
		_('Total') + ':Currency:100',
		_('Total after Taxes') + ':Currency:100',
		_('Returned') + ':Currency:100',
		_('Paid') + ':Currency:100',
		_('Remained') + ':Currency:100',
		_('1st Week') + ':Currency:100',
		_('2nd Week') + ':Currency:100',
		_('3th Week') + ':Currency:100',
		_('4th Week') + ':Currency:100',
		_('5th Week') + ':Currency:100'
	]

def get_data(filters):
	weeks_subquery = ''
	week_ranges = [(1, 7), (8, 14), (15, 21), (22, 28), (28, 31)]

	for k, v in enumerate(week_ranges):
		weeks_subquery += """
		(
			SELECT SUM(per.allocated_amount)
			FROM `tabPayment Entry Reference` AS `per`
			LEFT JOIN `tabPayment Entry` AS `pe` ON pe.name = per.parent
			WHERE pe.docstatus = 1
			AND pe.payment_type = 'Receive'
			AND pe.party_type = 'Customer'
			AND pe.party = si.customer
			AND per.reference_doctype = 'Sales Invoice'
			AND YEAR(pe.posting_date) = Year(si.posting_date)
			AND MONTH(pe.posting_date) = MONTH(si.posting_date)
			AND DAY(pe.posting_date) BETWEEN {0} AND {1}
			{conditions}
			GROUP BY YEAR(pe.posting_date), MONTH(pe.posting_date)
		) AS 'paid_w{2}',
		""".format(v[0], v[1], k + 1, conditions = get_conditions_for_weeks_subquery(filters))

	data = frappe.db.sql(
		"""
		SELECT
			posting_year,
			posting_month,
			customer,
			customer_name,
			customer_group,
			territory,
			credit_limit,
			payment_terms,
			sales_person,
			total,
			rounded_total,
			IFNULL(returned, 0.0) AS 'returned',
			rounded_total - outstanding_amount + IFNULL(returned, 0.0) AS 'paid',
			outstanding_amount,
			paid_w1,
			paid_w2,
			paid_w3,
			paid_w4,
			paid_w5
		FROM (
			SELECT
				si.customer,
				c.customer_name,
				c.customer_group,
				c.territory,
				c.credit_limit,
				c.payment_terms,
				st.sales_person,
				SUM(si.total) AS 'total',
				SUM(si.rounded_total) AS 'rounded_total',
				(
					SELECT SUM(si2.total)
					FROM `tabSales Invoice` AS `si2`
					WHERE si2.docstatus = 1
					AND si2.is_return = 1
					AND si2.customer = si.customer
					AND YEAR(si2.posting_date) = Year(si.posting_date)
					AND MONTH(si2.posting_date) = MONTH(si.posting_date)
					{conditions}
					GROUP BY YEAR(si2.posting_date), MONTH(si2.posting_date)
				) AS 'returned',
				SUM(si.outstanding_amount) AS 'outstanding_amount',
				{weeks_subquery}
				Year(si.posting_date) AS 'posting_year',
				MONTH(si.posting_date) AS 'posting_month'
			FROM `tabSales Invoice` AS `si`
			LEFT JOIN `tabCustomer` AS `c` ON c.name = si.customer
			LEFT JOIN `tabSales Team` AS `st` ON st.parent = si.name
			WHERE si.docstatus = 1
			AND si.is_return = 0
			{conditions}
			GROUP BY si.customer, st.sales_person, posting_year, posting_month
			ORDER BY posting_year, posting_month, si.customer, sales_person
		) AS `cffsw`
		""".format(weeks_subquery = weeks_subquery, conditions = get_conditions(filters)),
		filters
	)

	return data

def get_conditions(filters):
	conditions = ""

	if filters.get('company'):
		conditions += " AND si.company = %(company)s"

	if filters.get('business_unit'):
		conditions += " AND si.business_unit = %(business_unit)s"

	if filters.get('year'):
		conditions += " AND Year(si.posting_date) = %(year)s"

	if filters.get('month_from'):
		conditions += " AND MONTH(si.posting_date) >= %(month_from)s"

	if filters.get('month_to'):
		conditions += " AND MONTH(si.posting_date) <= %(month_to)s"

	if filters.get('customer'):
		conditions += " AND si.customer = %(customer)s"

	if filters.get('customer_group'):
		conditions += " AND c.customer_group = %(customer_group)s"

	if filters.get('sales_person'):
		conditions += " AND st.sales_person = %(sales_person)s"

	return conditions

def get_conditions_for_weeks_subquery(filters):
	conditions = ""

	if filters.get('company'):
		conditions += " AND pe.company = %(company)s"

	if filters.get('business_unit'):
		conditions += " AND pe.business_unit = %(business_unit)s"

	return conditions
