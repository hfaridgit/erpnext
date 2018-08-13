# -*- coding: utf-8 -*-
# Copyright (c) 2015, ESS LLP and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr, nowdate, nowtime, today


@frappe.whitelist()
def get_location_details():
	result = frappe.db.sql("""select c.name as customer, c.customer_name, sp.employee, e.user_id from `tabSales Team` st
		left join `tabCustomer` c on st.parent=c.name
		left join `tabSales Person` sp on st.sales_person=sp.name
		left join `tabEmployee` e on e.name=sp.employee
		where e.user_id=%s and isnull(c.latitude) and isnull(c.longitude)
		order by c.name
		""", (frappe.session.user), as_dict=True)
	
	return result

@frappe.whitelist()
def check(customer, latitude=None, longitude=None):
	if latitude and longitude:
		cust = frappe.get_doc("Customer", customer)
		cust.latitude = latitude
		cust.longitude = longitude
		cust.save()
	else:
		frappe.msgprint(
			_("The Location is not Defined."),
			title="Error", indicator="red"
		)
		
	
	
