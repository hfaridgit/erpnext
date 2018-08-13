# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import datetime
import random

import frappe
from frappe.model.delete_doc import delete_doc

# For test purposes only
# bench --site test execute 'erpnext.selling.doctype.sales_forecast.demo.setup'

class Demo(object):
	def __init__(self):
		super(Demo, self).__init__()

		self.company = 'Mifad'
		self.owner = 'm.ibrahim@egdirection.com'
		self.doctypes = ['Sales Invoice', 'Sales Forecast', 'Sales Forecast Period Status', 'Sales Forecast Period']
		self.series = ['SFC', 'SFCP', 'SFCPS']
		self.years = [2018, 2019]
		self.customers = ['CUST-1000000002', 'CUST-1000000003', 'CUST-1000000004']
		self.business_units = ['B2B', 'B2C']
		self.items = ['SFC/A', 'SFC/B', 'SFC/C']
		self.sales_persons = ['SFC Emp1', 'SFC Emp2']

		self.set_filters()
		frappe.set_user(self.owner)

	def set_filters(self):
		self.filters = {'company': self.company}

		if self.owner:
			self.filters['owner'] = self.owner

	def setup(self):
		self.destroy()
		self.reset_naming_series()
		self.create()

	def destroy(self):
		for doctype in self.doctypes:
			docs = frappe.db.get_all(doctype, self.filters)

			for doc in docs:
				delete_doc(doctype, doc.name, for_reload=True, ignore_on_trash=True)

	def reset_naming_series(self):
		frappe.db.sql(
			"UPDATE `tabSeries` SET current = 0 WHERE name IN ({})".format(
				', '.join(['%s'] * len(self.series))
			),
			self.series
		)

	def create(self):
		for year in self.years:
			self.create_sales_invoices(year)
			self.create_sales_forecast_period(year)

	def create_sales_invoices(self, year):
		for i in range(0, 20):
			si = frappe.new_doc('Sales Invoice')

			si.naming_series = 'SINV-'
			si.customer = random.choice(self.customers)
			si.posting_date = '{}-{}-{}'.format(year - 1, random.randint(1, 12), random.randint(1, 28))
			si.due_date = datetime.datetime.strptime(si.posting_date, '%Y-%m-%d') + datetime.timedelta(days=30)
			si.company = self.company
			si.business_unit = random.choice(self.business_units)
			si.posting_time = '00:00:00'
			si.set_posting_time = 1
			si.selling_price_list = 'Sales Forecast {}'.format(year)
			si.letter_head = 'Default'

			for i in range(0, random.randint(1, 5)):
				si.append('items', {
					'item_code': random.choice(self.items),
					'qty': random.randrange(10, 100, 10)
				})

			sales_person = frappe.db.get_value(
				'Sales Team',
				{'parent': si.customer, 'parenttype': 'Customer', 'parentfield': 'sales_team', 'idx': 1},
				'sales_person'
			)

			if sales_person:
				si.append('sales_team', {
					'sales_person': sales_person,
					'allocated_percentage': 100
				})

			si.submit()

	def create_sales_forecast_period(self, year):
		sfcp = frappe.new_doc('Sales Forecast Period')

		sfcp.company = self.company
		sfcp.business_unit = self.business_units[0]
		sfcp.price_list = 'Sales Forecast {}'.format(year)
		sfcp.year = year
		sfcp.q1_end_date = '{}-03-31'.format(year)
		sfcp.q2_end_date = '{}-06-30'.format(year)
		sfcp.q3_end_date = '{}-09-30'.format(year)
		sfcp.q4_end_date = '{}-12-31'.format(year)

		sfcp.submit()
		self.create_sales_forecast_period_status(sfcp)
		self.update_sales_forecasts(sfcp)

	def create_sales_forecast_period_status(self, sfcp):
		sfcps = frappe.new_doc('Sales Forecast Period Status')

		sfcps.sales_forecast_period = sfcp.name
		sfcps.company = sfcp.company
		sfcps.business_unit = sfcp.business_unit
		sfcps.price_list = sfcp.price_list
		sfcps.year = sfcp.year
		sfcps.sales_person = random.choice(self.sales_persons)
		sfcps.q1_end_date = sfcp.q1_end_date
		sfcps.q2_end_date = sfcp.q2_end_date
		sfcps.q3_end_date = sfcp.q3_end_date
		sfcps.q4_end_date = sfcp.q4_end_date
		sfcps.q1_status = random.choice(['Open', 'Closed'])
		sfcps.q2_status = random.choice(['Open', 'Closed'])
		sfcps.q3_status = random.choice(['Open', 'Closed'])
		sfcps.q4_status = random.choice(['Open', 'Closed'])

		sfcps.submit()

	def update_sales_forecasts(self, sfcp):
		if sfcp.year == self.years[0]:
			frappe.db.sql("UPDATE `tabSales Forecast` SET docstatus = 1")
			frappe.db.sql("UPDATE `tabSales Forecast Month` SET qty = FLOOR(1 + rand() * 10) * 100")

@frappe.whitelist()
def setup():
	Demo().setup()
