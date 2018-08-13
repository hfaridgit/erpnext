# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import datetime

import frappe

from erpnext.selling.sales_forecast_common import SalesForecastCommon

class SalesForecastPeriod(SalesForecastCommon):
	def validate(self):
		self.validate_year()
		self.validate_uniqueness(self.get_filters())

	def get_filters(self):
		filters = {
			'name': ['!=', self.name],
			'year': self.year
		}

		if self.sales_person:
			filters['sales_person'] = self.sales_person

		return filters
