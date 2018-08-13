# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document

class ChangeLeaveApproverTool(Document):
	pass


@frappe.whitelist()
def get_employees(approver=None, department = None, branch = None, company = None, business_unit = None):
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
	marked_list = frappe.db.sql("""select parent as employee, leave_approver as approver   
					from `tabEmployee Leave Approver` where leave_approver=%s""", (approver), as_dict=1)
	#for emp in frappe.get_list("Shift Changes", fields=["employee", "shift"],
	#						   filters={"posting_date": date}):
	for emp in marked_list:
		marked_employee[emp['employee']] = emp['approver'] 

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
def mark_employee_approver(employee_list, approver):
	employee_list = json.loads(employee_list)
	for employee in employee_list:
		emp = frappe.get_doc("Employee", employee['employee'])
		i = 0
		for app in emp.leave_approvers:
			if app.leave_approver == approver:
				i = 1
				
		if i == 0:
			emp.append("leave_approvers", {
						'leave_approver': approver
					})
					

		emp.save()

@frappe.whitelist()
def unmark_employee_approver(approver=None, department = None, branch = None, company = None, business_unit = None):
	employee_list = get_employees(approver, department, branch, company, business_unit)
	for employee in employee_list['marked']:
		emp = frappe.get_doc("Employee", employee['employee'])
		d = emp.get("leave_approvers", {
			"leave_approver": approver
		})
		if d:
			emp.get("leave_approvers").remove(d[0])
			emp.save()
