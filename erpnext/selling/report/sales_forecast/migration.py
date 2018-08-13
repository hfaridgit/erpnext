# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import frappe
from frappe.exceptions import DoesNotExistError

# Run:
# bench --site test execute 'erpnext.selling.report.sales_forecast.migration.migrate'

def migrate():
	try:
		doc = frappe.get_doc('Report', 'Sales Forecast')
	except DoesNotExistError:
		doc = frappe.new_doc('Report')

	doc.report_name = 'Sales Forecast'
	doc.ref_doctype = 'Sales Forecast'
	doc.module = 'Selling'
	doc.is_standard = 'Yes'
	doc.add_total_row = 0
	doc.report_type = 'Script Report'
	doc.disabled = 0
	doc.query = None

	doc.save()
