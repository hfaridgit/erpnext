# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate, now_datetime, add_days, getdate, today, fmt_money, add_to_date, DATE_FORMAT
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.model.naming import make_autoname
from frappe.model.document import Document

class EmployeeTransactionsTool(Document):
	def autoname(self):
		self.name = make_autoname(self.company + '/' + self.business_unit + '/' + str(self.transaction_year) + '-' + str(self.transaction_month) + '/.###')
		
	def validate(self):
		from erpnext.setup.doctype.business_unit.business_unit import validate_bu
		validate_bu(self)

	def get_employees(self):
		cond = ""
		conditions, values = [], []
		for field in ["company", "business_unit", "employment_type", "branch", "designation", "department", "employee"]:
			if self.get(field):
				conditions.append("{0}=%s".format(field))
				values.append(self.get(field))
				cond += " and " + field + "='" + self.get(field) + "'"

		condition_str = " and " + " and ".join(conditions) if len(conditions) else ""

		e = frappe.db.sql("select name from tabEmployee where status='Active' {condition}"
			.format(condition=condition_str), tuple(values))

		return cond
		
	def get_transactions_period(self):
		if self.branch:
			hr_settings = frappe.get_doc("Branch", self.branch)
			if not (hr_settings.transactions_end_day and hr_settings.transactions_start_day):
				hr_settings = frappe.get_doc("Business Unit", self.business_unit)
		else:
			hr_settings = frappe.get_doc("Business Unit", self.business_unit)
		if not (hr_settings.transactions_end_day and hr_settings.transactions_start_day):
			hr_settings = frappe.get_doc("HR Settings", "HR Settings")
			if not (hr_settings.transactions_end_day and hr_settings.transactions_start_day):
				frappe.throw(_("Transactions Period Start or End Day not Defined."))
		start_day = str(self.transaction_year if self.transaction_month > 1 else (self.transaction_year - 1)) + "-" + ("0" + str((self.transaction_month - 1) if self.transaction_month > 1 else 12))[-2:] + "-" + ("0" + hr_settings.transactions_start_day)[-2:]
		end_day = str(self.transaction_year) + "-" + ("0" + str(self.transaction_month))[-2:] + "-" + ("0" + hr_settings.transactions_end_day)[-2:]

		return start_day, end_day
		
	def delete_month_transactions(self):
		cond = self.get_employees()
		#start_day, end_day = self.get_transactions_period()
		#self.delete_punishments_unposted()
		frappe.db.sql("""Delete from `tabEmployee Punishment` 
			where transaction_year=%(trans_year)s and transaction_month=%(trans_month)s and is_auto_generated=1 
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'trans_year': self.transaction_year, 'trans_month': self.transaction_month})
		del_trans = frappe.db.sql("""Delete from `tabEmployee Transactions` 
			where transaction_year=%(trans_year)s and transaction_month=%(trans_month)s 
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'trans_year': self.transaction_year, 'trans_month': self.transaction_month})

		frappe.db.commit()
		self.last_generate_date = None
		frappe.db.set_value(self.doctype, self.name, "last_generate_date", None)

		frappe.msgprint(_("Transactions Deleted Successfuly."))
		
		
	def submit_month_transactions(self):
		cond = self.get_employees()
		#start_day, end_day = self.get_transactions_period()
		self.update_overtime()
		self.apply_punishments()
		smt_trans = frappe.db.sql("""update `tabEmployee Transactions` set docstatus=1 
			where transaction_year=%(trans_year)s and transaction_month=%(trans_month)s and payroll_processed=0 
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'trans_year': self.transaction_year, 'trans_month': self.transaction_month})

		frappe.db.sql("""update `tabEmployee Transactions Tool` set submitted=1 where name=%(name)s""",	{'name': self.name})	
			
		frappe.db.commit()
		
		frappe.msgprint(_("Transactions Submitted Successfuly."))
		
	def reopen_month_transactions(self):
		cond = self.get_employees()
		#self.delete_punishments()
		frappe.db.sql("""Delete from `tabEmployee Punishment` 
			where transaction_year=%(trans_year)s and transaction_month=%(trans_month)s and is_auto_generated=1 
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'trans_year': self.transaction_year, 'trans_month': self.transaction_month})
		smt_trans = frappe.db.sql("""update `tabEmployee Transactions` set docstatus=0 
			where transaction_year=%(trans_year)s and transaction_month=%(trans_month)s and payroll_processed=0 
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'trans_year': self.transaction_year, 'trans_month': self.transaction_month})

		frappe.db.sql("""update `tabEmployee Transactions Tool` set submitted=0 where name=%(name)s""",	{'name': self.name})	
			
		frappe.db.commit()
		
		frappe.msgprint(_("Transactions Re-Opened Successfuly."))
		
	def generate_month_transactions(self):
		cond = self.get_employees()
		start_day, end_day = self.get_transactions_period()
		
		frappe.db.sql("""insert ignore into `tabEmployee Transactions` (name, creation, modified, modified_by, owner, docstatus, idx, posting_date, day_name
			, employee, employee_name, transaction_year, transaction_month)
			(select concat(e.name, '/', x.selected_date), now(), now(), %(user)s, %(user)s, 0, day(x.selected_date), 
			x.selected_date, dayname(x.selected_date), e.name, e.employee_name, year(%(end_day)s), month(%(end_day)s) 
			from (
			select selected_date, 0 as docstatus from 
			(select adddate(concat(%(yyyy)s, '-01-01'),t2*100 + t1*10 + t0) selected_date from 
			 (select 0 t0 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t0,
			 (select 0 t1 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t1,
			 (select 0 t2 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t2) v
			where selected_date>=%(start_day)s and selected_date<=%(end_day)s) x
			left join `tabEmployee` e on e.docstatus=x.docstatus and e.status='Active'
			where e.name in (select name from `tabEmployee` where status='Active' {condition}))""".format(condition=cond),
			{'yyyy': self.transaction_year - 1, 'start_day': start_day, 'end_day': end_day, 'user': frappe.session.user})

		frappe.db.commit()
		self.update_transactions()
		# self.last_generate_date = now_datetime()
		frappe.db.set_value(self.doctype, self.name, "last_generate_date", now_datetime())
		frappe.msgprint(_("Transactions Created Successfuly."))
		
	def regenerate_month_transactions(self):
		cond = self.get_employees()
		start_day, end_day = self.get_transactions_period()
		frappe.db.sql("""Delete from `tabEmployee Transactions` 
			where transaction_year=%(trans_year)s and transaction_month=%(trans_month)s 
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'trans_year': self.transaction_year, 'trans_month': self.transaction_month})

		frappe.db.commit()

		frappe.db.sql("""insert ignore into `tabEmployee Transactions` (name, creation, modified, modified_by, owner, docstatus, idx, posting_date, day_name
			, employee, employee_name, transaction_year, transaction_month)
			(select concat(e.name, '/', x.selected_date), now(), now(), %(user)s, %(user)s, 0, day(x.selected_date), 
			x.selected_date, dayname(x.selected_date), e.name, e.employee_name, year(%(end_day)s), month(%(end_day)s) 
			from (
			select selected_date, 0 as docstatus from 
			(select adddate(concat(%(yyyy)s, '-01-01'),t2*100 + t1*10 + t0) selected_date from 
			 (select 0 t0 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t0,
			 (select 0 t1 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t1,
			 (select 0 t2 union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t2) v
			where selected_date>=%(start_day)s and selected_date<=%(end_day)s) x
			left join `tabEmployee` e on e.docstatus=x.docstatus and e.status='Active'
			where e.name in (select name from `tabEmployee` where status='Active' {condition}))""".format(condition=cond), 
			{'yyyy': self.transaction_year - 1, 'start_day': start_day, 'end_day': end_day, 'user': frappe.session.user})

		frappe.db.commit()
		self.update_transactions()
		# self.last_generate_date = now_datetime()
		frappe.db.set_value(self.doctype, self.name, "last_generate_date", now_datetime())
		frappe.msgprint(_("Transactions Regenerated Successfuly."))
		
	def update_generated_transactions(self):
		self.update_transactions(self.last_generate_date)
		frappe.msgprint(_("Transactions Updated Successfuly."))
		
	def apply_punishments(self):
		trans = frappe.db.sql("""select et.name, et.employee, et.shift, et.posting_date, et.lateness_minutes, et.early_exit_minutes, et.bus_delay, 
							if(time(et.shift_late_time)<et.time_in, TIMESTAMPDIFF(MINUTE, time(et.shift_late_time), et.time_in),0) as lateness, 
							ifnull(p.total_units,0)*60 as permit_minutes, p.is_early_leave 
							from `tabEmployee Transactions` et 
							left join `tabPermit Application` p on p.name=et.permit_application 
							where et.docstatus=0 and (et.lateness_minutes>0 
							or et.early_exit_minutes>0) and et.ignore_lateness=0 and et.transaction_year=%(trans_year)s and et.transaction_month=%(trans_month)s""", 
							{"trans_year": self.transaction_year, "trans_month": self.transaction_month}, as_dict=1)
		for t in trans:
			if not t.shift:
				frappe.throw(_("No Shift Defined for Employee {0}.").format(t.employee))
			shift_type = frappe.db.get_value("Shifts", t.shift, "shift_type")
			if not shift_type:
				shift_type = ""
			if t.is_early_leave == 1:
				permit_minutes = 0
				permit_minutes2 = t.permit_minutes
			else:
				permit_minutes = t.permit_minutes
				permit_minutes2 = 0
			actual_late_minutes = t.lateness_minutes - permit_minutes
			if t.lateness > 0 and actual_late_minutes > 0 and t.bus_delay == 0:
				punishment = frappe.db.sql("""select name, punishment_type from `tabPunishment Rule` 
							where rule_type='Lateness' and (shift_type=%(shift_type)s or isnull(shift_type)) 
							and from_m<=%(late_mintues)s and to_m>=%(late_mintues)s order by shift_type DESC limit 1""", 
							{"late_mintues": actual_late_minutes, "shift_type": shift_type}, as_dict=1)
				if punishment:
					p = frappe.new_doc('Employee Punishment')
					p.posting_date = t.posting_date
					p.employee = t.employee
					p.punishment_name = punishment[0].name
					p.punishment_type = punishment[0].punishment_type
					p.company = self.company
					p.business_unit = self.business_unit
					p.is_auto_generated = 1
					p.transaction_month = self.transaction_month
					p.transaction_year = self.transaction_year
					p.insert()
					p.submit()
					frappe.db.set_value("Employee Transactions", t.name, "punishment", p.name)
					frappe.db.set_value("Employee Transactions", t.name, "punishment_name", p.punishment_name)
				else:
					frappe.throw(_("No Punishment Rules Defined for Lateness to Apply."))
			
			actual_late_minutes = t.early_exit_minutes - permit_minutes2
			if actual_late_minutes > 0:
				punishment = frappe.db.sql("""select name, punishment_type from `tabPunishment Rule` 
							where rule_type='Early Exit' and (shift_type=%(shift_type)s or isnull(shift_type)) 
							order by shift_type DESC limit 1""", 
							{"shift_type": shift_type}, as_dict=1)
				if punishment:
					p = frappe.new_doc('Employee Punishment')
					p.posting_date = t.posting_date
					p.employee = t.employee
					p.punishment_name = punishment[0].name
					p.punishment_type = punishment[0].punishment_type
					p.company = self.company
					p.business_unit = self.business_unit
					p.is_auto_generated = 1
					p.transaction_month = self.transaction_month
					p.transaction_year = self.transaction_year
					p.insert()
					p.submit()
					frappe.db.set_value("Employee Transactions", t.name, "punishment", p.name)
					frappe.db.set_value("Employee Transactions", t.name, "punishment_name", p.punishment_name)
				else:
					frappe.throw(_("No Punishment Rules Defined for Early Exit to Apply."))
					
		trans = frappe.db.sql("""select * from (
								select et.name, et.employee, et.shift, et.posting_date, et.ignore_lateness, et.is_holiday, et.is_leave, 
								if(length(mission_application)>1,1,0) as is_mission, 
								if(isnull(et.time_in) and isnull(et.time_out),3,if(isnull(et.time_in),1,if(isnull(et.time_out),2,0))) as no_punch, 
								s.apply_absent, s.absent_punishment_rule, s.in_out_punishment_rule
								from `tabEmployee Transactions` et
								left join `tabShifts` s on s.name=et.shift
								where et.docstatus=0 
								and et.transaction_year=%(trans_year)s and et.transaction_month=%(trans_month)s) a
								where  no_punch>0 and is_holiday=0 and is_leave=0 and is_mission=0""", 
								{"trans_year": self.transaction_year, "trans_month": self.transaction_month}, as_dict=1)
		for t in trans:
			if not t.shift:
				frappe.throw(_("No Shift Defined for Employee {0}.").format(t.employee))
			if t.no_punch < 3:
				punishment_rule = t.in_out_punishment_rule if t.in_out_punishment_rule else None
			else:
				punishment_rule = t.absent_punishment_rule if t.absent_punishment_rule else None
			
			if punishment_rule:
				punishment = frappe.db.sql("""select name, punishment_type from `tabPunishment Rule` 
							where name=%(punishment_rule)s""", 
							{"punishment_rule": punishment_rule}, as_dict=1)
						
			if punishment and punishment_rule:
				p = frappe.new_doc('Employee Punishment')
				p.posting_date = t.posting_date
				p.employee = t.employee
				p.punishment_name = punishment_rule
				p.punishment_type = punishment[0].punishment_type
				p.company = self.company
				p.business_unit = self.business_unit
				p.is_auto_generated = 1
				p.transaction_month = self.transaction_month
				p.transaction_year = self.transaction_year
				p.insert()
				p.submit()
				frappe.db.set_value("Employee Transactions", t.name, "punishment", p.name)
				frappe.db.set_value("Employee Transactions", t.name, "punishment_name", p.punishment_name)
				

	def delete_punishments_unposted(self):
		trans = frappe.db.sql("""select name, punishment from `tabEmployee Transactions` where (lateness_minutes>0 or early_exit_minutes>0) 
							and ignore_lateness=0 and transaction_year=%(trans_year)s and transaction_month=%(trans_month)s
							and payroll_processed=0 and not isnull(punishment)""", 
							{"trans_year": self.transaction_year, "trans_month": self.transaction_month}, as_dict=1)
		for t in trans:
			frappe.db.set_value("Employee Transactions", t.name, "punishment", None)
			frappe.db.set_value("Employee Transactions", t.name, "punishment_name", None)
			p = frappe.get_doc('Employee Punishment', t.punishment)
			#p.flags.ignore_permissions = True
			p.cancel()
			#p.delete()
		
		trans = frappe.db.sql("""select name, punishment from `tabEmployee Transactions` where (ifnull(time_in,0)=0 or ifnull(time_out,0)=0) 
							and transaction_year=%(trans_year)s and transaction_month=%(trans_month)s
							and payroll_processed=0 and not isnull(punishment)""", 
							{"trans_year": self.transaction_year, "trans_month": self.transaction_month}, as_dict=1)
		for t in trans:
			frappe.db.set_value("Employee Transactions", t.name, "punishment", None)
			frappe.db.set_value("Employee Transactions", t.name, "punishment_name", None)
			p = frappe.get_doc('Employee Punishment', t.punishment)
			#p.flags.ignore_permissions = True
			p.cancel()
			#p.delete()
		frappe.db.commit()

	def delete_punishments(self):
		trans = frappe.db.sql("""select name, punishment from `tabEmployee Transactions` where docstatus=1 and (lateness_minutes>0 or early_exit_minutes>0) 
							and ignore_lateness=0 and transaction_year=%(trans_year)s and transaction_month=%(trans_month)s
							and payroll_processed=0 and not isnull(punishment)""", 
							{"trans_year": self.transaction_year, "trans_month": self.transaction_month}, as_dict=1)
		for t in trans:
			frappe.db.set_value("Employee Transactions", t.name, "punishment", None)
			frappe.db.set_value("Employee Transactions", t.name, "punishment_name", None)
			p = frappe.get_doc('Employee Punishment', t.punishment)
			#p.flags.ignore_permissions = True
			p.cancel()
			#p.delete()

		trans = frappe.db.sql("""select name, punishment from `tabEmployee Transactions` where docstatus=1 and (ifnull(time_in,0)=0 or ifnull(time_out,0)=0) 
							and transaction_year=%(trans_year)s and transaction_month=%(trans_month)s
							and payroll_processed=0 and not isnull(punishment)""", 
							{"trans_year": self.transaction_year, "trans_month": self.transaction_month}, as_dict=1)
		for t in trans:
			frappe.db.set_value("Employee Transactions", t.name, "punishment", None)
			frappe.db.set_value("Employee Transactions", t.name, "punishment_name", None)
			p = frappe.get_doc('Employee Punishment', t.punishment)
			#p.flags.ignore_permissions = True
			p.cancel()
			#p.delete()
		frappe.db.commit()

	def update_transactions(self, starting_date=None):
		start_day, end_day = self.get_transactions_period()
		if not starting_date:
			starting_date = "1900-01-01"
		cond = self.get_employees()
		leaves = frappe.db.sql("""select * from `tabLeave Application`  
			where ((from_date>=%(start_day)s and from_date<=%(end_day)s) or (to_date>=%(start_day)s and to_date<=%(end_day)s)
			 or (half_day_date>=%(start_day)s and half_day_date<=%(end_day)s)) and docstatus=1 and status='Approved' and modified>%(starting_date)s
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'start_day': start_day, 'end_day': end_day, 'starting_date': starting_date}, as_dict=1)
			
		############# Leaves 
		
		for lv in leaves:
			leave_date = lv.from_date
			if lv.leave_type_type == "Mission":
				while leave_date <= lv.to_date:
					if getdate(leave_date) >= getdate(start_day) and getdate(leave_date) <= getdate(end_day):
						frappe.db.sql("""update `tabEmployee Transactions` set mission_application=%(name)s , half_day=if(posting_date=%(hdd)s,%(hd)s,0)
							where docstatus=0 
							and employee=%(employee)s and posting_date=%(leave_date)s""", {'name': lv.name, 'employee': lv.employee, 'leave_date': leave_date, 
							'hd': lv.half_day, 'hdd':lv.half_day_date})
					leave_date = add_days(leave_date, 1)
			else:
				while leave_date <= lv.to_date:
					if getdate(leave_date) >= getdate(start_day) and getdate(leave_date) <= getdate(end_day):
						frappe.db.sql("""update `tabEmployee Transactions` set is_leave=1, leave_type=%(leave_type)s, leave_application=%(name)s, half_day=if(posting_date=%(hdd)s,%(hd)s,0) 
							where docstatus=0 
							and employee=%(employee)s and posting_date=%(leave_date)s""", {'name': lv.name, 'employee': lv.employee, 'leave_date': leave_date, 
							'hd': lv.half_day, 'hdd':lv.half_day_date, 'leave_type': lv.leave_type})
					leave_date = add_days(leave_date, 1)
			
		############# permits 
		
		permits = frappe.db.sql("""select * from `tabPermit Application`  
			where (permit_date>=%(start_day)s and permit_date<=%(end_day)s) and docstatus=1 and status='Approved' and modified>%(starting_date)s
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'start_day': start_day, 'end_day': end_day, 'starting_date': starting_date}, as_dict=1)
			
		for p in permits:
			frappe.db.sql("""update `tabEmployee Transactions` set permit_application=%(name)s, permit_hours=%(total_units)s 
				where docstatus=0 
				and employee=%(employee)s and posting_date=%(permit_date)s""", {'name': p.name, 'employee': p.employee, 
				'permit_date': p.permit_date, 'total_units': p.total_units})

		############# Route Attendance 
		
		employees = frappe.db.sql("""select name, route from `tabEmployee`  
			where employee in (select name from tabEmployee where status='Active' {condition})""".format(condition=cond),  as_dict=1)
			
		for emp in employees:
			frappe.db.sql("""update `tabEmployee Transactions` et
					left join `tabRoute Attendance` ra on et.posting_date=ra.transaction_date and ra.route_name=%s and ra.docstatus=1 
					left join `tabRoute` r on r.name=ra.route_name
					set et.bus_time_in=time(ra.time_in), et.bus_delay=if(timediff(time(ra.time_in),r.default_time_in)>'00:05:00',1,0) 
					where et.employee=%s and et.docstatus=0 and not isnull(ra.time_in)""", 
					(emp.route, emp.name))
					
		############# punishments 
		
		punishments = frappe.db.sql("""select * from `tabEmployee Punishment`  
			where (posting_date>=%(start_day)s and posting_date<=%(end_day)s) and docstatus=1 and modified>%(starting_date)s 
			and employee in (select name from `tabEmployee` where status='Active' {condition})""".format(condition=cond), 
			{'start_day': start_day, 'end_day': end_day, 'starting_date': starting_date}, as_dict=1)
			
		for p in punishments:
			frappe.db.sql("""update `tabEmployee Transactions` set punishment=%(name)s, punishment_name=%(p_name)s
				where docstatus=0 
				and employee=%(employee)s and posting_date=%(posting_date)s""", {'name': p.name, 'employee': p.employee, 
				'posting_date': p.posting_date, 'p_name': p.punishment_name})

		############# Attendance 
		
		frappe.db.sql("""update `tabEmployee Transactions` et
				left join `tabAttendance` att on att.employee=et.employee and att.attendance_date=et.posting_date
				set et.time_in=att.time_in, et.time_out=att.time_out, et.attendance_hours=timediff(att.time_out, att.time_in)
				where et.docstatus=0 and att.modified>%(starting_date)s 
				and et.employee in (select name from `tabEmployee` where status='Active' {condition}) 
				and et.posting_date>=%(start_day)s and et.posting_date<=%(end_day)s""".format(condition=cond), { 
				'start_day': start_day, 'end_day': end_day, 'starting_date': starting_date})
				
		############# shifts 
		
		shifts = frappe.db.sql("""select s.employee, s.posting_date, s.shift, sh.ignore_lateness, sh.* from `tabShift Changes` s
			left join `tabShifts` sh on s.shift=sh.name
			where (s.posting_date>=%(start_day)s and s.posting_date<=%(end_day)s) and s.docstatus=1 and s.modified>%(starting_date)s 
			and s.employee in (select name from `tabEmployee` where status='Active' {condition}) 
			order by s.posting_date, s.modified""".format(condition=cond), 
			{'start_day': start_day, 'end_day': end_day, 'starting_date': starting_date}, as_dict=1)
			
		for sh in shifts:
			frappe.db.sql("""update `tabEmployee Transactions` set shift=%(shift)s, ignore_lateness=%(ls)s, enable_overtime=%(ot)s, 
				overtime_minutes=if(time(%(end_time)s)<time_out, TIMESTAMPDIFF(MINUTE, time(%(end_time)s), time_out),0), 
				lateness_minutes=if(time(%(start_time)s)<time_in, TIMESTAMPDIFF(MINUTE, time(%(start_time)s), time_in),0), 
				early_exit_minutes=if(time_out<time(%(end_time)s), TIMESTAMPDIFF(MINUTE, time_out, time(%(end_time)s)), 0), shift_late_time = %(late_time)s
				where docstatus=0 
				and employee=%(employee)s and posting_date>=%(posting_date)s""", {'shift': sh.shift, 'employee': sh.employee, 'posting_date': sh.posting_date, 
				'ls': sh.ignore_lateness, 'ot': sh.enable_overtime, 'end_time': sh.end_time, 'start_time': sh.start_time, 'late_time': sh.late_time})
		
		frappe.db.sql("""update `tabEmployee Transactions` et 
				left join `tabEmployee` e on e.name=et.employee 
				left join `tabShifts` sh on sh.name=e.shift
				set et.shift=e.shift, et.ignore_lateness=ifnull(sh.ignore_lateness,0), et.enable_overtime=ifnull(sh.enable_overtime,0), 
				et.overtime_minutes=if(sh.end_time<et.time_out, ifnull(TIMESTAMPDIFF(MINUTE, sh.end_time, et.time_out),0),0), 
				et.lateness_minutes=if(sh.start_time<et.time_in, ifnull(TIMESTAMPDIFF(MINUTE, sh.start_time, et.time_in),0),0), 
				et.early_exit_minutes=if(et.time_out<sh.end_time, ifnull(TIMESTAMPDIFF(MINUTE, et.time_out, sh.end_time),0),0), shift_late_time=sh.late_time
				where et.docstatus=0 and isnull(et.shift)
				and et.posting_date>=%(start_day)s and et.posting_date<=%(end_day)s""", {  
				'start_day': start_day, 'end_day': end_day})
	
		############# Holiday 
		
		frappe.db.sql("""update `tabEmployee Transactions` et 
				left join `tabEmployee` e on e.name=et.employee
				left join `tabShifts` s on s.name=et.shift
				left join `tabHoliday` h1 on h1.parent=s.holiday_list and et.posting_date=h1.holiday_date
				left join `tabHoliday` h2 on h2.parent=e.holiday_list and et.posting_date=h2.holiday_date
				set et.is_holiday=if(isnull(h1.holiday_date) and isnull(h2.holiday_date), 0, 1)
				where et.docstatus=0 
				and et.employee in (select name from `tabEmployee` where status='Active' {condition}) 
				and et.posting_date>=%(start_day)s and et.posting_date<=%(end_day)s""".format(condition=cond), { 
				'start_day': start_day, 'end_day': end_day})
		self.update_overtime()

		frappe.db.commit()
				
	def update_overtime(self):
		cond = self.get_employees()
		start_day, end_day = self.get_transactions_period()
	
		frappe.db.sql("""update `tabEmployee Transactions` set  
			overtime_minutes=TIMESTAMPDIFF(MINUTE, time_in, time_out), 
			lateness_minutes=0, 
			early_exit_minutes=0
			where docstatus=0 and is_holiday=1 and not isnull(time_in) and not isnull(time_out)
			and employee in (select name from `tabEmployee` where status='Active' {condition}) 
			and posting_date>=%(start_day)s and posting_date<=%(end_day)s""".format(condition=cond), { 
			'start_day': start_day, 'end_day': end_day})
			
		frappe.db.sql("""update `tabEmployee Transactions` et 
			left join `tabShifts` s on s.name=et.shift
			set et.overtime_minutes=if(s.end_time<et.time_out and TIMESTAMPDIFF(MINUTE, s.end_time, et.time_out)>s.minutes_after, 
									TIMESTAMPDIFF(MINUTE, s.end_time, et.time_out),0) + 
								 if(s.start_time>et.time_in and TIMESTAMPDIFF(MINUTE, et.time_in, s.start_time)>s.minutes_before, 
									TIMESTAMPDIFF(MINUTE, et.time_in, s.start_time),0)
			where et.docstatus=0 and et.is_holiday<>1 and not isnull(et.time_in) and not isnull(et.time_out)
			and employee in (select name from `tabEmployee` where status='Active' {condition}) 
			and posting_date>=%(start_day)s and posting_date<=%(end_day)s""".format(condition=cond), { 
			'start_day': start_day, 'end_day': end_day})

@frappe.whitelist()
def change_shift(posting_date, employee, shift, company, business_unit):
	sh = frappe.new_doc('Shift Changes')
	sh.posting_date = posting_date
	sh.employee = employee
	sh.shift = shift
	sh.company = company
	sh.business_unit = business_unit
	sh.insert()
	sh.submit()
	
	x_date = frappe.db.sql("""select posting_date from `tabShift Changes` s
		where posting_date>%(posting_date)s and docstatus=1 
		and employee=%(employee)s 
		order by s.posting_date ASC limit 1""",	{'employee': employee, 'posting_date': posting_date}, as_dict=1)
	
	if not x_date:
		next_date = "2999-12-31"
	else:
		next_date = x_date[0].posting_date
		
	shf = frappe.get_doc("Shifts", shift)
		
	frappe.db.sql("""update `tabEmployee Transactions` set shift=%(shift)s, ignore_lateness=%(ls)s, enable_overtime=%(ot)s, 
		overtime_minutes=if(time(%(end_time)s)<time_out, TIMESTAMPDIFF(MINUTE, time(%(end_time)s), time_out),0), 
		lateness_minutes=if(time(%(start_time)s)<time_in, TIMESTAMPDIFF(MINUTE, time(%(start_time)s), time_in),0), 
		early_exit_minutes=if(time_out<time(%(end_time)s), TIMESTAMPDIFF(MINUTE, time_out, time(%(end_time)s)),0), shift_late_time = %(late_time)s
		where docstatus=0 
		and employee=%(employee)s and posting_date>=%(posting_date)s and posting_date<%(next_date)s""", {'shift': shift, 'employee': employee, 
		'posting_date': posting_date, 'next_date': next_date, 
		'ls': shf.ignore_lateness, 'ot': shf.enable_overtime, 'end_time': shf.end_time, 'start_time': shf.start_time, 'late_time': shf.late_time})
		
	############# Adjust Holiday according to Shift change
	
	frappe.db.sql("""update `tabEmployee Transactions` et 
			left join `tabEmployee` e on e.name=et.employee
			left join `tabShifts` s on s.name=et.shift
			left join `tabHoliday` h1 on h1.parent=s.holiday_list and et.posting_date=h1.holiday_date
			left join `tabHoliday` h2 on h2.parent=e.holiday_list and et.posting_date=h2.holiday_date
			set et.is_holiday=if(isnull(h1.holiday_date) and isnull(h2.holiday_date), 0, 1)
			where et.docstatus=0 
			and et.employee=%(employee)s 
			and et.posting_date>=%(start_day)s""", {'start_day': posting_date, 'employee': employee})
		
@frappe.whitelist()
def change_time(posting_date, employee, shift, fieldname, key_name, new_value):
	frappe.db.set_value("Employee Transactions", key_name, fieldname, new_value)
	shf = frappe.get_doc("Shifts", shift)
	frappe.db.sql("""update `tabEmployee Transactions` set attendance_hours=timediff(time_out, time_in), 
		overtime_minutes=if(time(%(end_time)s)<time_out,TIMESTAMPDIFF(MINUTE, time(%(end_time)s), time_out),0), 
		lateness_minutes=if(time(%(start_time)s)<time_in,TIMESTAMPDIFF(MINUTE, time(%(start_time)s), time_in),0), 
		early_exit_minutes=if(time_out<time(%(end_time)s),TIMESTAMPDIFF(MINUTE, time_out, time(%(end_time)s)),0), shift_late_time = %(late_time)s
		where docstatus=0 
		and employee=%(employee)s and posting_date=%(posting_date)s""", {'employee': employee, 
		'posting_date': posting_date, 'end_time': shf.end_time, 'start_time': shf.start_time, 'late_time': shf.late_time})
	
	frappe.db.commit()
	
@frappe.whitelist()
def change_permit(permit_date, employee, total_units, company, business_unit, is_early_leave=0):
	pmt = frappe.new_doc('Permit Application')
	pmt.permit_date = permit_date
	pmt.posting_date = today()
	pmt.status = "Approved"
	pmt.leave_approver = frappe.session.user
	pmt.is_early_leave = is_early_leave
	pmt.employee = employee
	pmt.total_units = flt(total_units)
	pmt.company = company
	pmt.business_unit = business_unit
	pmt.insert()
	pmt.submit()
	frappe.db.sql("""update `tabEmployee Transactions` set permit_application=%(name)s, permit_hours=%(total_units)s  
					where docstatus=0 and employee=%(employee)s and posting_date=%(permit_date)s""", 
					{"name": pmt.name, "employee": employee, "permit_date": permit_date, "total_units": total_units})
	
@frappe.whitelist()
def change_leave(from_date, to_date, leave_type, naming_series, employee, company, business_unit, half_day=0):
	lv_type = frappe.get_value("Leave Type", leave_type, "leave_type")
	lv = frappe.new_doc('Leave Application')
	lv.naming_series = naming_series
	lv.leave_type_type = lv_type
	lv.from_date = from_date
	lv.to_date = to_date
	lv.posting_date = today()
	lv.leave_type = leave_type
	lv.status = "Approved"
	lv.leave_approver = frappe.session.user
	lv.employee = employee
	lv.half_day = half_day
	lv.company = company
	lv.business_unit = business_unit
	lv.insert()
	lv.submit()
	if leave_type == "مأمورية":
		frappe.db.sql("""update `tabEmployee Transactions` set mission_application=%(name)s, half_day=%(half_day)s
						where docstatus=0 and employee=%(employee)s and posting_date>=%(from_date)s and posting_date<=%(to_date)s""", 
						{"name": lv.name, "half_day": half_day, "employee": employee, "from_date": from_date, "to_date": to_date})
	else:
		frappe.db.sql("""update `tabEmployee Transactions` set leave_application=%(name)s, half_day=%(half_day)s, is_leave=1, leave_type=%(leave_type)s  
						where docstatus=0 and employee=%(employee)s and posting_date>=%(from_date)s and posting_date<=%(to_date)s""", 
						{"name": lv.name, "half_day": half_day, "employee": employee, "from_date": from_date, "to_date": to_date, "leave_type": leave_type})
	
@frappe.whitelist()
def leave_query(doctype, txt, searchfield, start, page_len, filters):
	leave_types = frappe.db.sql("""select name from (select leave_type as name from `tabLeave Allocation` 
					where docstatus=1 and employee=%(employee)s and from_date<=%(posting_date)s and to_date>=%(posting_date)s
					union all
					select name from `tabLeave Type` where leave_type='Occasional Leave') a
					where (name like %(txt)s)
					limit %(start)s, %(page_len)s""", 
					{
						'txt': "%%%s%%" % txt,
						'start': start,
						'page_len': page_len,
						'employee': filters.get('employee'),
						'posting_date': filters.get('posting_date')
					})
	return leave_types

