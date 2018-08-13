# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import frappe

# Run:
# bench --site test execute 'erpnext.selling.sales_forecast_migration.migrate'

def migrate():
	module = 'selling'
	doctype = 'doctype'
	names = ['sales_forecast', 'sales_forecast_item', 'sales_forecast_period']

	for name in names:
		frappe.reload_doc(module, doctype, name, True, True)
