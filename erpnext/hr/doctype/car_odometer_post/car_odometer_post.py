# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today
from frappe.model.document import Document

class CarOdometerPost(Document):
	def validate(self):
		if not self.company:
			frappe.throw(_("Company is missing."))
		if not self.business_unit:
			frappe.throw(_("Business Unit is missing."))
		if not self.posting_date:
			frappe.throw(_("Posting Date is missing."))
		if not self.salary_slip_type:
			frappe.throw(_("Salary Slip Type is missing."))
		
	def post_transactions(self):
		self.validate()
		transactions = frappe.db.sql("""select employee, employee_name, sum(total_counter) as counter from `tabCar Odometer Register`
							where docstatus=1 and ifnull(status,'')<>'Processed' and end_date<=%s 
							and employee in (select name from `tabEmployee` where status='Active' and company=%s and business_unit=%s)
							group by employee""", (self.posting_date, self.company, self.business_unit), as_dict=1)
		sst = frappe.get_doc("Salary Slip Type", self.salary_slip_type)
		sst.employees = []
		if transactions:
			for d in transactions:
				sst.append('employees', {
					'employee': d.employee, 
					'employee_name': d.employee_name, 
					'counter': d.counter
				})
		sst.save()
		frappe.db.sql("""update `tabCar Odometer Register` set status='Posted'
							where docstatus=1 and ifnull(status,'')<>'Processed' and end_date<=%s""", (self.posting_date))
		frappe.msgprint(_("Transactions Posted Successfuly."))
		
	def get_transactions(self):
		self.validate()
		start_dt = frappe.db.sql("""select ifnull(max(md.date), '1990-01-01') as start_date
									from `tabMission Details Actual` md 
									left join `tabMission Actual` ma on ma.name=md.parent
									where md.docstatus<>2 and md.holiday=0 and md.is_submitted=1
									and ma.company=%(company)s and ma.business_unit=%(business_unit)s""", 
									{'company': self.company, 'business_unit': self.business_unit}, as_dict=1)

		transactions = frappe.db.sql("""select ma.employee, ma.employee_name, max(md.car_number) as car_number, sum(md.km_car_to - md.km_car_from) as total_counter, 
										min(md.date) as start_date, max(md.date) as end_date
										from `tabMission Details Actual` md 
										left join `tabMission Actual` ma on ma.name=md.parent
										where md.docstatus<>2 and md.holiday=0 and md.is_submitted=0 
										and ma.company=%(company)s and ma.business_unit=%(business_unit)s 
										and md.date>%(start_date)s and md.date<=%(end_date)s
										group by employee having total_counter<>0""", {'company': self.company, 'business_unit': self.business_unit, 
										'start_date': start_dt[0].start_date, 'end_date': self.posting_date}, as_dict=1)
										
		missions = frappe.db.sql("""select ma.employee, ma.employee_name, ma.company, ma.business_unit, md.date
										from `tabMission Details Actual` md 
										left join `tabMission Actual` ma on ma.name=md.parent
										where md.docstatus<>2 and md.holiday=0 and md.is_submitted=0 
										and (not isnull(md.mission_place_1) or not isnull(md.mission_place_2) or not isnull(md.mission_place_3) 
										or not isnull(md.mission_place_4) or not isnull(md.mission_place_5) or not isnull(md.mission_place_6) 
										or not isnull(md.mission_place_7) or not isnull(md.mission_place_8) or not isnull(md.mission_place_9) or not isnull(md.mission_place_10)) 
										and ma.company=%(company)s and ma.business_unit=%(business_unit)s 
										and md.date>%(start_date)s and md.date<=%(end_date)s
										""", {'company': self.company, 'business_unit': self.business_unit, 
										'start_date': start_dt[0].start_date, 'end_date': self.posting_date}, as_dict=1)
										
		if transactions:
			for d in transactions:
				com = frappe.new_doc("Car Odometer Register")
				com.employee = d.employee
				com.employee_name = d.employee_name
				com.car_number = d.car_number
				com.start_date = d.start_date
				com.end_date = d.end_date
				com.total_counter = d.total_counter
				com.insert()
				com.submit()
				
		if missions:
			for m in missions:
				lv = frappe.new_doc('Leave Application')
				lv.naming_series = '_MIS/'
				lv.leave_type_type = 'Mission'
				lv.from_date = m.date
				lv.to_date = m.date
				lv.posting_date = today()
				lv.leave_type = 'مأمورية'
				lv.status = "Approved"
				lv.leave_approver = frappe.session.user
				lv.employee = m.employee
				lv.company = m.company
				lv.business_unit = m.business_unit
				lv.follow_via_email = 0
				lv.insert()
				lv.submit()
		
		frappe.db.sql("""update `tabMission Details Actual` md 
						left join `tabMission Actual` ma on ma.name=md.parent
						set md.is_submitted=1
						where md.docstatus<>2 and md.holiday=0 and md.is_submitted=0 
						and ma.company=%(company)s and ma.business_unit=%(business_unit)s 
						and md.date>%(start_date)s and md.date<=%(end_date)s""", 
						{'company': self.company, 'business_unit': self.business_unit, 
						'start_date': start_dt[0].start_date, 'end_date': self.posting_date})
						
		frappe.msgprint(_("Odometer Register and Missions Created Successfuly for this period."))
		
