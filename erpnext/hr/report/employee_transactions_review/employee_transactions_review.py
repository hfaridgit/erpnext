# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns(filters)
	return columns, data

def get_filter_condition(filters):
	cond = ''
	for f in filters:
		if f == 'year':
			cond += " and transaction_year = " + str(filters.get(f))
		else:
			if f == 'month':
				cond += " and transaction_month = " + str(filters.get(f))
			else:
				cond += " and " + f + " = '" + filters.get(f).replace("'", "\'") + "'"

	return cond

def get_data(filters):
	cond = get_filter_condition(filters)
	data = frappe.db.sql("""select * from ( 
							select e.company, e.business_unit, e.branch, et.name, et.docstatus, et.posting_date, et.day_name, et.employee, et.employee_name, ifnull(left(et.time_in,5),"___") as time_in, ifnull(left(et.time_out,5),"___") as time_out, 
									ifnull(left(et.attendance_hours,5),"___") as attendance_hours, et.lateness_minutes as lateness_minutes2, et.overtime_minutes as overtime_minutes2, et.early_exit_minutes as early_exit_minutes2, 
									ifnull(et.mission_application,"___") as mission_application,  if(et.bus_delay=1,'&#10003;','___') as bus_delay,  if(et.is_holiday=1,'&#10003;','___') as is_holiday, 
									if(et.is_leave=1,'&#10003;','___') as is_leave,  ifnull(et.shift,"___") as shift, ifnull(et.leave_application ,"___") as leave_application, 
									et.leave_type, ifnull(et.permit_application,"___") as permit_application, et.permit_hours,  et.punishment, et.punishment_name,  
									if(et.half_day=1,'&#10003;','___') as half_day,  ifnull(left(et.bus_time_in,5),"___") as bus_time_in,  
									if(et.ignore_lateness=1,'&#10003;','___') as ignore_lateness,  if(et.enable_overtime=1,'&#10003;','___') as enable_overtime, 
									et.shift_late_time, e.image, et.transaction_year, et.transaction_month, et.lateness_minutes, et.overtime_minutes, et.early_exit_minutes  
									from `tabEmployee Transactions` et left join `tabEmployee` e on e.name=et.employee) a
									where 1=1 %s 
									order by length(name),name""" % (cond), as_dict=True)

	return data

def get_columns(filters):
	return [
		{
			"fieldname": "company",
			"label": _("company"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "business_unit",
			"label": _("business_unit"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "branch",
			"label": _("barnch"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "name",
			"label": _("name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "docstatus",
			"label": _("docstatus"),
			"fieldtype": "Int",
			"hidden": 1
		},
		{
			"fieldname": "posting_date",
			"label": _("Date"),
			"fieldtype": "Link",
			"actualtype": "Date",
			"options": "HHH",
			"actualoptions": "",
			"width": 80
		},
		{
			"fieldname": "day_name",
			"label": _("day_name"),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 80
		},
		{
			"fieldname": "employee",
			"label": _("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"actualoptions": "Employee",
			"width": 250
		},
		{
			"fieldname": "employee_name",
			"label": _("Employee Name"),
			"hidden": 1
		},
		{
			"fieldname": "time_in",
			"label": _("IN"),
			"fieldtype": "Link",
			"actualtype": "Time",
			"options": "HHH",
			"actualoptions": "",
			"width": 40
		},
		{
			"fieldname": "time_out",
			"label": _("OUT"),
			"fieldtype": "Link",
			"actualtype": "Time",
			"options": "HHH",
			"actualoptions": "",
			"width": 40
		},
		{
			"fieldname": "attendance_hours",
			"label": _("Hours"),
			"fieldtype": "Link",
			"actualtype": "Time",
			"options": "HHH",
			"actualoptions": "",
			"width": 50
		},
		{
			"fieldname": "lateness_minutes2",
			"label": _("Late"),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 40
		},
		{
			"fieldname": "overtime_minutes2",
			"label": _("OT"),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 50
		},
		{
			"fieldname": "early_exit_minutes2",
			"label": _("Early"),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 40
		},
		{
			"fieldname": "mission_application",
			"label": _("Mission"),
			"fieldtype": "Link",
			"actualtype": "Link",
			"options": "Leave Application",
			"actualoptions": "Leave Application",
			"width": 70
		},
		{
			"fieldname": "bus_delay",
			"label": _("Bus Delay"),
			"fieldtype": "Link",
			"actualtype": "Check",
			"options": "HHH",
			"actualoptions": "",
			"width": 80
		},
		{
			"fieldname": "is_holiday",
			"label": _("Holiday"),
			"fieldtype": "Link",
			"actualtype": "Check",
			"options": "HHH",
			"actualoptions": "",
			"width": 40
		},
		{
			"fieldname": "is_leave",
			"label": _("Leave"),
			"fieldtype": "Link",
			"actualtype": "Check",
			"options": "HHH",
			"actualoptions": "",
			"width": 50
		},
		{
			"fieldname": "shift",
			"label": _("Shift"),
			"fieldtype": "Link",
			"options": "Shifts",
			"actualoptions": "Shifts",
			"width": 120
		},
		{
			"fieldname": "leave_application",
			"label": _("Leave App."),
			"fieldtype": "Link",
			"options": "Leave Application",
			"actualoptions": "Leave Application",
			"width": 120
		},
		{
			"fieldname": "leave_type",
			"label": _("Leave Type"),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 120
		},
		{
			"fieldname": "permit_application",
			"label": _("Permit"),
			"fieldtype": "Link",
			"actualtype": "Link",
			"options": "Permit Application",
			"actualoptions": "Permit Application",
			"width": 120
		},
		{
			"fieldname": "permit_hours",
			"label": _("Permit Hours"),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 120
		},
		{
			"fieldname": "punishment",
			"label": _("Punishment"),
			"fieldtype": "Link",
			"options": "Employee Punishment",
			"width": 120
		},
		{
			"fieldname": "punishment_name",
			"label": _("Punishment Name"),
			"fieldtype": "Link",
			"actualtype": "Data",
			"options": "HHH",
			"actualoptions": "",
			"width": 120
		},
		{
			"fieldname": "half_day",
			"label": _("Half Day"),
			"fieldtype": "Link",
			"actualtype": "Check",
			"options": "HHH",
			"actualoptions": "",
			"width": 80
		},
		{
			"fieldname": "bus_time_in",
			"label": _("Bus IN"),
			"fieldtype": "Link",
			"actualtype": "Time",
			"options": "HHH",
			"actualoptions": "",
			"width": 80
		},
		{
			"fieldname": "ignore_lateness",
			"label": _("Ignore Late"),
			"fieldtype": "Link",
			"actualtype": "Check",
			"options": "HHH",
			"actualoptions": "",
			"width": 80
		},
		{
			"fieldname": "enable_overtime",
			"label": _("Enable OT"),
			"fieldtype": "Link",
			"actualtype": "Check",
			"options": "HHH",
			"actualoptions": "",
			"width": 80
		}, 
		{
			"fieldname": "shift_late_time",
			"label": _("Shift Late Time"),
			"fieldtype": "Time",
			"hidden": 1
		}, 
		{
			"fieldname": "image",
			"label": _("image"),
			"fieldtype": "Data",
			"hidden": 1
		}, 
		{
			"fieldname": "transaction_year",
			"label": _("Year"),
			"fieldtype": "Int",
			"hidden": 1
		}, 
		{
			"fieldname": "transaction_month",
			"label": _("Month"),
			"fieldtype": "Int",
			"hidden": 1
		}, 
		{
			"fieldname": "lateness_minutes",
			"label": _("Min. Late"),
			"fieldtype": "Int",
			"hidden": 1
		},
		{
			"fieldname": "overtime_minutes",
			"label": _("Min. OT"),
			"fieldtype": "Int",
			"hidden": 1
		},
		{
			"fieldname": "early_exit_minutes",
			"label": _("Early Min."),
			"fieldtype": "Int",
			"hidden": 1
		},
	]

@frappe.whitelist()
def get_employees(company, branch):
	return frappe.db.sql("""select name from `tabEmployee` where status='Active' and company=%s and branch=%s
					order by length(name), name""", (company, branch))
