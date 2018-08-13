# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import datetime

import frappe
from frappe import _
from frappe.model.document import Document

class SalesForecastCommon(Document):
	def validate_year(self):
		current_year = datetime.date.today().year

		if (self.year < current_year):
			frappe.throw(_('Year must be greater than or equal to {}'.format(current_year)))

	def validate_uniqueness(self, filters):
		existing_doc = frappe.get_value(self.doctype, filters)

		if existing_doc:
			frappe.throw(_('{} already exists: {}'.format(
				self.doctype,
				'<a href="#Form/{0}/{1}">{1}</a>'.format(self.doctype, existing_doc)
			)))
