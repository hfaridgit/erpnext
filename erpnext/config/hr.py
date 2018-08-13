from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Employee and Attendance"),
			"items": [
				{
					"type": "doctype",
					"name": "Employee",
					"description": _("Employee records."),
				},
				{
					"type": "doctype",
					"name": "Employee Attendance Tool",
					"label": _("Employee Attendance Tool"),
					"description":_("Mark Attendance for multiple employees"),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Employee Transactions Tool",
					"label": _("Employee Transactions Tool"),
					"description":_("Prepare Monthly Transactions for employees"),
					"hide_count": True
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Transactions Review",
					"doctype": "Employee Transactions"
				},
				{
					"type": "doctype",
					"name": "Attendance",
					"description": _("Attendance record."),
				},
				{
					"type": "doctype",
					"name": "Route",
					"label": _("Bus Routes"),
					"description": _("Bus Master data."),
				},
				{
					"type": "page",
					"name": "bus_attendance",
					"label": _("Bus Attendance"),
					"description": _("Bus Attendance record."),
				},
				{
					"type": "doctype",
					"name": "Route Attendance",
					"label": _("Bus Attendance Edit"),
					"description": _("Bus Attendance Edit."),
				},
				{
					"type": "doctype",
					"name": "Permit Application",
					"description": _("Application for Permit."),
				},
				{
					"type": "doctype",
					"name": "Shift Changes",
					"description": _("Shifts Changes."),
				},
				{
					"type": "doctype",
					"name": "Change Shift Tool",
					"description": _("Shifts Changes Tool."),
				},
				{
					"type": "doctype",
					"name": "Change Leave Approver Tool",
					"description": _("Leave Approver Changes Tool."),
				},
				{
					"type": "doctype",
					"name": "Upload Attendance",
					"description":_("Upload attendance from a .csv file"),
					"hide_count": True
				},
			]
		},
		{
			"label": _("Recruitment"),
			"items": [
				{
					"type": "doctype",
					"name": "Job Applicant",
					"description": _("Applicant for a Job."),
				},
				{
					"type": "doctype",
					"name": "Job Opening",
					"description": _("Opening for a Job."),
				},
				{
					"type": "doctype",
					"name": "Offer Letter",
					"description": _("Offer candidate a Job."),
				},
			]
		},
		{
			"label": _("Leaves and Holiday"),
			"items": [
				{
					"type": "doctype",
					"name": "Leave Application",
					"description": _("Applications for leave."),
				},
				{
					"type": "doctype",
					"name":"Leave Type",
					"description": _("Type of leaves like casual, sick etc."),
				},
				{
					"type": "doctype",
					"name": "Holiday Name",
					"description": _("Holiday Name master.")
				},
				{
					"type": "doctype",
					"name": "Holiday List",
					"description": _("Holiday master.")
				},
				{
					"type": "doctype",
					"name": "Holiday Changes",
					"description": _("Make Bulk changes in Holidays lists.")
				},
				{
					"type": "doctype",
					"name": "Leave Allocation",
					"description": _("Allocate leaves for a period.")
				},
				{
					"type": "doctype",
					"name": "Leave Control Panel",
					"label": _("Leave Allocation Tool"),
					"description":_("Allocate leaves for the year."),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Annual Leave Allocation",
					"label": _("Leave Allocation Tool for all Employees"),
					"description":_("All Employees and all Leave Types."),
					"hide_count": True 
				},
				{
					"type": "doctype",
					"name": "Leave Block List",
					"description": _("Block leave applications by department.")
				},

			]
		},
		{
			"label": _("Payroll"),
			"items": [
				{
					"type": "doctype",
					"name": "Salary Slip",
					"description": _("Monthly salary statement."),
				},
				{
					"type": "doctype",
					"name": "Payroll Entry",
					"label": _("Payroll Entry"),
					"description":_("Generate Salary Slips"),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Salary Structure",
					"description": _("Salary template master.")
				},
				{
					"type": "doctype",
					"name": "Salary Calculator",
					"description": _("Calculate Net or Gross Salary.")
				},
				{
					"type": "doctype",
					"name": "Salary Component",
					"label": _("Salary Components"),
					"description": _("Earnings, Deductions and other Salary components")
				},
				{
					"type": "doctype",
					"name": "Salary Slip Type",
					"label": _("Salary Slip Type"),
					"description": _("Normal Salary Slip or Bonus or Other Payment Slip")
				},

			]
		},
		{
			"label": _("Expense Claims"),
			"items": [
				{
					"type": "doctype",
					"name": "Employee Advance",
					"description": _("Manage advance amount given to the Employee"),
				},
				{
					"type": "doctype",
					"name": "Expense Claim",
					"description": _("Claims for company expense."),
				},
				{
					"type": "doctype",
					"name": "Expense Claim Type",
					"description": _("Types of Expense Claim.")
				},
			]
		},
		{
			"label": _("Appraisals"),
			"items": [
				{
					"type": "doctype",
					"name": "Appraisal",
					"description": _("Performance appraisal."),
				},
				{
					"type": "doctype",
					"name": "Appraisal Template",
					"description": _("Template for performance appraisals.")
				},
				{
					"type": "page",
					"name": "team-updates",
					"label": _("Team Updates")
				},
			]
		},
		{
			"label": _("Employee Loan Management"),
			"icon": "icon-list",
			"items": [
				{
					"type": "doctype",
					"name": "Loan Type",
					"description": _("Define various loan types")
				},
				{
					"type": "doctype",
					"name": "Employee Loan Application",
					"description": _("Employee Loan Application")
				},
				{
					"type": "doctype",
					"name": "Employee Loan"
				},
			]
		},
		{
			"label": _("Training"),
			"items": [
				{
					"type": "doctype",
					"name": "Training Program"
				},
				{
					"type": "doctype",
					"name": "Training Event"
				},
				{
					"type": "doctype",
					"name": "Training Result"
				},
				{
					"type": "doctype",
					"name": "Training Feedback"
				},
			]
		},

		{
			"label": _("Administration"),
			"items": [
				{
					"type": "doctype",
					"name": "Vehicle"
				},
				{
					"type": "doctype",
					"name": "Vehicle Log"
				},
				{
					"type": "doctype",
					"name": "Official Documents"
				},
				{
					"type": "doctype",
					"name": "Custody Type"
				},
				{
					"type": "doctype",
					"name": "Employee Custody"
				},
				{
					"type": "doctype",
					"name": "Car Odometer Register"
				},
				{
					"type": "doctype",
					"name": "Car Odometer Post"
				},
			]
		},
		{
			"label": _("Setup"),
			"icon": "fa fa-cog",
			"items": [
				{
					"type": "doctype",
					"name": "HR Settings",
					"description": _("Settings for HR Module")
				},
				{
					"type": "doctype",
					"name": "Permit Settings",
					"description": _("Settings for Permits")
				},
				{
					"type": "doctype",
					"name": "Employment Type",
					"description": _("Types of employment (permanent, contract, intern etc.).")
				},
				{
					"type": "doctype",
					"name": "Shifts",
					"description": _("Shifts Settings.")
				},
				{
					"type": "doctype",
					"name": "Branch",
					"description": _("Organization branch master.")
				},
				{
					"type": "doctype",
					"name": "Department",
					"description": _("Organization unit (department) master.")
				},
				{
					"type": "doctype",
					"name": "Designation",
					"description": _("Employee designation (e.g. CEO, Director etc.).")
				},
				{
					"type": "doctype",
					"name": "Job",
					"label": _("Organization Chart"),
					"route": "Tree/Job",
					"description": _("Tree of Jobs."),
				},
				{
					"type": "doctype",
					"name": "Daily Work Summary Settings"
				},
			]
		},
		{
			"label": _("Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Leave Balance",
					"doctype": "Leave Application"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Birthday",
					"doctype": "Employee"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employees working on a holiday",
					"doctype": "Employee"
				},
				{
					"type": "report",
					"name": "Employee Information",
					"doctype": "Employee"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Salary Register",
					"doctype": "Salary Slip"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Monthly Attendance Sheet",
					"doctype": "Attendance"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Vehicle Expenses",
					"doctype": "Vehicle"
				},

			]
		},
		{
			"label": _("Help"),
			"icon": "fa fa-facetime-video",
			"items": [
				{
					"type": "help",
					"label": _("Setting up Employees"),
					"youtube_id": "USfIUdZlUhw"
				},
				{
					"type": "help",
					"label": _("Leave Management"),
					"youtube_id": "fc0p_AXebc8"
				},
				{
					"type": "help",
					"label": _("Expense Claims"),
					"youtube_id": "5SZHJF--ZFY"
				},
				{
					"type": "help",
					"label": _("Processing Payroll"),
					"youtube_id": "apgE-f25Rm0"
				},
			]
		},
		{
			"label": _("Punishments"),
			"icon": "fa fa-file-powerpoint-o",
			"items": [
				{
					"type": "doctype",
					"label": _("Administrative Punishment Names"),
					"name": "Punishment Admin Action",
					"description": ""
				},
				{
					"type": "doctype",
					"label": _("Punishment Rules Setup"),
					"name": "Punishment Rule",
					"description": ""
				},
				{
					"type": "doctype",
					"label": _("Employee Punishment"),
					"name": "Employee Punishment",
					"description": ""
				},
			]
		}
	]
