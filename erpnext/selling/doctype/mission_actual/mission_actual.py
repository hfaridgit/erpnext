# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class MissionActual(Document):
	def autoname(self):
		if not self.employee:
			frappe.throw(_("Employee is not Defined."))
		self.name = self.employee + '/' + self.year + '-' + self.week

	def validate(self):
		if not self.employee:
			frappe.throw(_("Employee is not Defined."))
		if self.get("__islocal"):
			days = self.get_week_days()
			self.mission_details = []
			for d in days:
				self.append("mission_details", 
					{
						"date": d.day_date,
						"day": d.day_name,
					})
			
	def get_week_days(self):
		week_date = "STR_TO_DATE(concat(" + self.year + "," + self.week + ",' 0'), '%X%V %w')"
		hhh = """SELECT @d:={0} as wd, dayname(DATE_ADD(@d, INTERVAL 0 DAY)) as day_name, date(DATE_ADD(@d, INTERVAL 0 DAY)) as day_date
					union all
					SELECT date(now()), dayname(DATE_ADD(@d, INTERVAL 1 DAY)), date(DATE_ADD(@d, INTERVAL 1 DAY))
					union all
					SELECT date(now()), dayname(DATE_ADD(@d, INTERVAL 2 DAY)), date(DATE_ADD(@d, INTERVAL 2 DAY))
					union all
					SELECT date(now()), dayname(DATE_ADD(@d, INTERVAL 3 DAY)), date(DATE_ADD(@d, INTERVAL 3 DAY))
					union all
					SELECT date(now()), dayname(DATE_ADD(@d, INTERVAL 4 DAY)), date(DATE_ADD(@d, INTERVAL 4 DAY))
					union all
					SELECT date(now()), dayname(DATE_ADD(@d, INTERVAL 5 DAY)), date(DATE_ADD(@d, INTERVAL 5 DAY))
					union all
					SELECT date(now()), dayname(DATE_ADD(@d, INTERVAL 6 DAY)), date(DATE_ADD(@d, INTERVAL 6 DAY))""".format(week_date)
		return frappe.db.sql(hhh, as_dict=1)
