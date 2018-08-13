# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, getdate, formatdate
from frappe import throw, _
from frappe.model.document import Document
import datetime
from dateutil import relativedelta
from datetime import timedelta

class HolidayChanges(Document):
	def on_submit(self):
		self.validate_values()
		if self.apply_to_all:
			for d in frappe.db.sql("""select name from `tabHoliday List`"""):
				holiday_list = d[0]
				if not self.delete_holiday:
					self.make_holiday(holiday_list)
				else:
					self.del_all_holiday()
		else:
			if not self.delete_holiday:
				self.make_holiday(self.holiday_list)
			else:
				self.del_holiday()
			
		
	def validate_values(self):
		if not self.apply_to_all and not self.holiday_list:
			throw(_("Please select a Holiday List or Apply to All."))
		
		if not self.holiday_name:
			throw(_("Please select a Holiday Name."))
		
	def make_holiday(self, holiday_list):
		if holiday_list:
			hl = frappe.get_doc('Holiday List', holiday_list)
			if self.holiday_type == "Weekend":
				if not (getdate(hl.from_date) <= getdate(self.from_date)):
					hl.from_date = self.from_date
				if (getdate(hl.to_date) <= getdate(self.to_date)):
					hl.to_date = self.to_date
				x_from = hl.from_date
				x_to = hl.to_date
				hl.from_date = self.from_date
				hl.to_date = self.to_date
				hl.weekly_off = self.holiday_name
				hl.get_weekly_off_dates()
				hl.from_date = x_from
				hl.to_date = x_to
			if self.holiday_type == "Normal Off Day":
				self.normal_child(holiday_list, hl)
			if self.holiday_type == "Variable Off Day":
				self.variable_child(holiday_list, hl)
			
			hl.save()

	def normal_child(self, holiday_list, hl):
		date_list = []
		last_idx = max([cint(d.idx) for d in hl.get("holidays")] or [0,])
		existing_date_list = [getdate(holiday.holiday_date) for holiday in hl.get("holidays") if holiday.description == self.holiday_name]
		start_year = getdate(self.from_date).year
		end_year = getdate(self.to_date).year
		reference_year = start_year
		while reference_year <= end_year:
			start_date = datetime.date(reference_year, cint(self.from_month), cint(self.from_day))		
			end_date = datetime.date(reference_year, cint(self.to_month), cint(self.to_day))		
			reference_date = start_date
			while reference_date <= end_date:
				if reference_date not in existing_date_list:
					date_list.append(reference_date)
				reference_date += timedelta(days=1)
			reference_year += 1
		for i, d in enumerate(date_list):
			ch = hl.append('holidays', {})
			ch.description = self.holiday_name
			ch.holiday_date = d
			ch.idx = last_idx + i + 1
			
	def variable_child(self, holiday_list, hl):
		date_list = []
		last_idx = max([cint(d.idx) for d in hl.get("holidays")] or [0,])
		existing_date_list = [getdate(holiday.holiday_date) for holiday in hl.get("holidays") if holiday.description == self.holiday_name]
		start_date = getdate(self.from_date)		
		end_date = getdate(self.to_date)	
		reference_date = start_date
		while reference_date <= end_date:
			if reference_date not in existing_date_list:
				date_list.append(reference_date)
			reference_date += timedelta(days=1)
		for i, d in enumerate(date_list):
			ch = hl.append('holidays', {})
			ch.description = self.holiday_name
			ch.holiday_date = d
			ch.idx = last_idx + i + 1

	def del_all_holiday(self):
		frappe.db.sql("""delete from `tabHoliday` where description=%s and holiday_date>=%s and holiday_date<=%s""", 
				(self.holiday_name, self.from_date, self.to_date))

	def del_holiday(self):
		frappe.db.sql("""delete from `tabHoliday` where parent=%s and description=%s and holiday_date>=%s and holiday_date<=%s""", 
				(self.holiday_list, self.holiday_name, self.from_date, self.to_date))
	
	