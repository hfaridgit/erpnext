# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document

class ChangeShiftTool(Document):
	pass


@frappe.whitelist()
def get_employees(date, shift=None, department = None, branch = None, company = None, business_unit = None):
	employees_not_marked = []
	employees_marked = []
	filters = {"status": "Active"}
	if department != "All":
		filters["department"] = department
	if branch != "All":
		filters["branch"] = branch
	if company != "All":
		filters["company"] = company
	if business_unit != "All":
		filters["business_unit"] = business_unit

	employee_list = frappe.get_list("Employee", fields=["employee", "employee_name"], filters=filters, order_by="employee_name")
	marked_employee = {}
	marked_list = frappe.db.sql("""select employee, shift from (
					(select if(modified=max(modified), modified, null) as modified, if(modified=max(modified), posting_date, null) as posting_date, 
					if(modified=max(modified), employee, null) as employee, if(modified=max(modified), shift, null) as shift  
					from `tabShift Changes` where posting_date<=%s group by employee, posting_date, shift order by employee,modified desc)) a
					group by employee having shift=%s""", (date, shift), as_dict=1)
	#for emp in frappe.get_list("Shift Changes", fields=["employee", "shift"],
	#						   filters={"posting_date": date}):
	for emp in marked_list:
		marked_employee[emp['employee']] = emp['shift'] 

	for employee in employee_list:
		employee['status'] = marked_employee.get(employee['employee'])
		if employee['employee'] not in marked_employee:
			employees_not_marked.append(employee)
		else:
			employees_marked.append(employee)
	return {
		"marked": employees_marked,
		"unmarked": employees_not_marked
	}


@frappe.whitelist()
def mark_employee_shift(employee_list, shift, date, company=None, business_unit=None):
	employee_list = json.loads(employee_list)
	for employee in employee_list:
		sft = frappe.new_doc("Shift Changes")
		sft.employee = employee['employee']
		#sft.employee_name = employee['employee_name']
		sft.posting_date = date
		sft.shift = shift
		if company and company != "All":
			sft.company = company
		else:
			sft.company = frappe.db.get_value("Employee", employee['employee'], "Company")
		if business_unit and business_unit != "All":
			sft.business_unit = business_unit
		else:
			sft.business_unit = frappe.db.get_value("Employee", employee['employee'], "business_unit")
		#sft.insert()
		sft.submit()
