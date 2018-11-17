# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, math
from frappe import _
from frappe.utils import flt, rounded
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document

from erpnext.hr.doctype.employee_loan.employee_loan import get_monthly_repayment_amount, check_repayment_method

class EmployeeLoanApplication(Document):
	def validate(self):
		from erpnext.setup.doctype.business_unit.business_unit import validate_bu
		validate_bu(self)
		check_repayment_method(self.repayment_method, self.loan_amount, self.repayment_amount, self.repayment_periods)
		validate_loan_amount(self)
		self.get_repayment_details()

	def get_repayment_details(self):
		if self.repayment_method == "Repay Over Number of Periods":
			self.repayment_amount = get_monthly_repayment_amount(self.repayment_method, self.loan_amount, self.rate_of_interest, self.repayment_periods)

		if self.repayment_method == "Repay Fixed Amount per Period":
			monthly_interest_rate = flt(self.rate_of_interest) / (12 *100)
			if monthly_interest_rate:
				self.repayment_periods = math.ceil((math.log(self.repayment_amount) - 
					math.log(self.repayment_amount - (self.loan_amount*monthly_interest_rate))) /
					(math.log(1 + monthly_interest_rate)))
			else:
				self.repayment_periods = self.loan_amount / self.repayment_amount

		self.calculate_payable_amount()
		
	def calculate_payable_amount(self):
		balance_amount = self.loan_amount
		self.total_payable_amount = 0
		self.total_payable_interest = 0

		while(balance_amount > 0):
			interest_amount = rounded(balance_amount * flt(self.rate_of_interest) / (12*100))
			balance_amount = rounded(balance_amount + interest_amount - self.repayment_amount)

			self.total_payable_interest += interest_amount
			
		self.total_payable_amount = self.loan_amount + self.total_payable_interest

def validate_loan_amount(doc):
	maximum_loan_limit = frappe.db.get_value('Loan Type', doc.loan_type, 'maximum_loan_amount')
	previous_loan_amounts = frappe.db.sql("""SELECT sum(loan_amount) as loan_amount from `tabEmployee Loan` 
							where docstatus=1 and loan_type=%s and employee=%s and status in ("Sanctioned","Repaid/Closed")""", 
							(doc.loan_type, doc.employee))
	#frappe.throw(_("Previous Loan Amounts are {0}").format(previous_loan_amounts[0][0]))
	if maximum_loan_limit:
		maximum_loan_limit = flt(maximum_loan_limit) - flt(previous_loan_amounts[0][0])
	if maximum_loan_limit and doc.loan_amount > maximum_loan_limit:
		frappe.throw(_("Loan Amount cannot exceed Maximum Loan Amount of {0}").format(maximum_loan_limit))
		
@frappe.whitelist()
def make_employee_loan(source_name, target_doc = None):
	doclist = get_mapped_doc("Employee Loan Application", source_name, {
		"Employee Loan Application": {
			"doctype": "Employee Loan",
			"field_map": {
				"repayment_amount": "monthly_repayment_amount"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc)

	return doclist