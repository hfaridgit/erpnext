# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr, nowdate, nowtime, today


@frappe.whitelist()
def get_attendance_details():
	result = frappe.db.sql("""select route_name, if(date(last_check_in)=date(now()),last_check_in, null)  as time_in, 
		if(date(last_check_out)=date(now()),last_check_out, null) as time_out
		from `tabRoute`
		where enabled=1
		order by creation
		""", as_dict=True)
	
	return result

@frappe.whitelist()
def check(route_name, check_type):
	route_att1 = frappe.db.sql("""select * from `tabRoute Attendance` 
						where route_name=%s and transaction_date=%s""", (route_name, today()), as_dict=1)
	
	if not route_att1:
		route_att = frappe.new_doc("Route Attendance")
		route_att.route_name = route_name
		route_att.transaction_date = today()
		route_att.insert()
		route_att.submit()
		frappe.db.commit()
	else:
		route_att = route_att1[0]
	
	if cint(check_type) == 0:
		frappe.db.sql("""update `tabRoute Attendance` set time_in=time(now()) 
						where route_name=%s and transaction_date=%s""", (route_name, today()))
		frappe.db.sql("""update `tabRoute` set last_check_in=time(now()), last_route_attendance=%s, last_transaction_date=%s  
						where name=%s""", (route_att.name, today(), route_name))
	else:
		frappe.db.sql("""update `tabRoute Attendance` set time_out=time(now()) 
						where route_name=%s and transaction_date=%s""", (route_name, today()))
		frappe.db.sql("""update `tabRoute` set last_check_out=time(now()), last_route_attendance=%s, last_transaction_date=%s  
						where name=%s""", (route_att.name, today(), route_name))
		
	
	
