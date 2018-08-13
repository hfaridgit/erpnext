# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, formatdate, comma_and, time_diff_in_seconds, to_timedelta
from frappe.model.document import Document
from dateutil.parser import parse

class WorkstationHolidayError(frappe.ValidationError): pass
class NotInWorkingHoursError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass

class Workstation(Document):
	def validate(self):
		labour_rate = 0
		for labour in self.labours:
			labour_rate += flt(labour.hour_rate * labour.cost_percent / 100)
		self.hour_rate_labour = labour_rate
		costing = frappe.db.get_singles_dict('Costing Settings')
		self.hour_rate_electricity = self.electricity_consumption_per_hour * flt(costing.electricity_rate if costing.electricity_rate else 0)
		self.hour_rate_water = flt(self.water_consumption_per_hour * flt(costing.water_rate if costing.water_rate else 0))
		self.hour_rate_gas = flt(self.gas_consumption_per_hour * flt(costing.gas_rate if costing.gas_rate else 0))
		self.hour_rate = (flt(self.hour_rate_labour) + flt(self.hour_rate_electricity) + self.hour_rate_water + self.hour_rate_gas +
			flt(self.hour_rate_consumable) + flt(self.hour_rate_rent))

	def on_update(self):
		self.validate_overlap_for_operation_timings()
		self.update_bom_operation()

	def validate_overlap_for_operation_timings(self):
		"""Check if there is no overlap in setting Workstation Operating Hours"""
		for d in self.get("working_hours"):
			existing = frappe.db.sql_list("""select idx from `tabWorkstation Working Hour`
				where parent = %s and name != %s
					and (
						(start_time between %s and %s) or
						(end_time between %s and %s) or
						(%s between start_time and end_time))
				""", (self.name, d.name, d.start_time, d.end_time, d.start_time, d.end_time, d.start_time))

			if existing:
				frappe.throw(_("Row #{0}: Timings conflicts with row {1}").format(d.idx, comma_and(existing)), OverlapError)

	def update_bom_operation(self):
		bom_list = frappe.db.sql("""select DISTINCT parent from `tabBOM Operation`
			where workstation = %s""", self.name)

		for bom_no in bom_list:
			frappe.db.sql("""update `tabBOM Operation` set hour_rate = %s
				where parent = %s and workstation = %s""",
				(self.hour_rate, bom_no[0], self.name))

			bom = frappe.get_doc("BOM", bom_no[0])
			bom.update_cost()

@frappe.whitelist()
def get_default_holiday_list():
	return frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "default_holiday_list")

def check_if_within_operating_hours(workstation, operation, from_datetime, to_datetime):
	if from_datetime and to_datetime:
		if not cint(frappe.db.get_value("Manufacturing Settings", "None", "allow_production_on_holidays")):
			check_workstation_for_holiday(workstation, from_datetime, to_datetime)

		if not cint(frappe.db.get_value("Manufacturing Settings", None, "allow_overtime")):
			is_within_operating_hours(workstation, operation, from_datetime, to_datetime)

def is_within_operating_hours(workstation, operation, from_datetime, to_datetime):
	operation_length = time_diff_in_seconds(to_datetime, from_datetime)
	workstation = frappe.get_doc("Workstation", workstation)
	
	if not workstation.working_hours:
		return

	for working_hour in workstation.working_hours:
		if working_hour.start_time and working_hour.end_time:
			slot_length = (to_timedelta(working_hour.end_time or "") - to_timedelta(working_hour.start_time or "")).total_seconds()
			if slot_length >= operation_length:
				return

	frappe.throw(_("Operation {0} longer than any available working hours in workstation {1}, break down the operation into multiple operations").format(operation, workstation.name), NotInWorkingHoursError)

def check_workstation_for_holiday(workstation, from_datetime, to_datetime):
	holiday_list = frappe.db.get_value("Workstation", workstation, "holiday_list")
	if holiday_list and from_datetime and to_datetime:
		applicable_holidays = []
		for d in frappe.db.sql("""select holiday_date from `tabHoliday` where parent = %s
			and holiday_date between %s and %s """,
			(holiday_list, getdate(from_datetime), getdate(to_datetime))):
				applicable_holidays.append(formatdate(d[0]))

		if applicable_holidays:
			frappe.throw(_("Workstation is closed on the following dates as per Holiday List: {0}")
				.format(holiday_list) + "\n" + "\n".join(applicable_holidays), WorkstationHolidayError)
