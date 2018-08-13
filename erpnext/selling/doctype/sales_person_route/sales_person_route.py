# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.model.document import Document

class SalesPersonRoute(Document):
	def on_submit(self):
		for d in self.invoices:
			if d.sales_invoice and d.status:
				frappe.db.set_value('Sales Invoice', d.sales_invoice, 'invoice_status', d.status)
	
@frappe.whitelist()
def get_sales_person():
	employee = frappe.db.get_value('Employee', {'user_id': frappe.session.user, 'status': 'Active'})

	if employee:
		return frappe.db.get_value('Sales Person', {'employee': employee, 'enabled': 1})

@frappe.whitelist()
def customer_query(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	cust_master_name = frappe.defaults.get_user_default("cust_master_name")

	if cust_master_name == "Customer Name":
		fields = ["c.name", "c.customer_group", "c.territory"]
	else:
		fields = ["c.name", "c.customer_name", "c.customer_group", "c.territory"]

	meta = frappe.get_meta("Customer")
	searchfields = meta.get_search_fields()
	searchfields = searchfields + [f for f in [searchfield or "name", "customer_name"] \
			if not f in searchfields]
	searchfields = ["c." + f for f in searchfields]
	fields = fields + [f for f in searchfields if not f in fields]

	fields = ", ".join(fields)
	searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])

	return frappe.db.sql("""select {fields} from `tabSales Team` as `st`
		left join `tabCustomer` as `c` on c.name = st.parent
		where st.sales_person = '{sales_person}'
			and c.docstatus < 2
			and ({scond}) and c.disabled=0
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, c.name), locate(%(_txt)s, c.name), 99999),
			if(locate(%(_txt)s, c.customer_name), locate(%(_txt)s, c.customer_name), 99999),
			c.idx desc,
			c.name, c.customer_name
		limit %(start)s, %(page_len)s""".format(**{
			"fields": fields,
			"scond": searchfields,
			"mcond": get_match_cond(doctype),
			"fcond": get_filters_cond(doctype, filters, conditions).replace('%', '%%'),
			"sales_person": get_sales_person()
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})

@frappe.whitelist()
def invoice_query(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql("""select name, grand_total from `tabSales Invoice` 
					where customer=%(customer)s and docstatus=1 and invoice_status<>'تم تحصيل الفاتورة'
					and ({key} like %(txt)s)
					{fcond} {mcond}
					order by 
						if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
						name
					limit %(start)s, %(page_len)s""".format(**{
						'key': searchfield,
						'mcond':get_match_cond(doctype), 
						"fcond": get_filters_cond(doctype, filters, conditions).replace('%', '%%')
					}), {
						'txt': "%%%s%%" % txt,
						'_txt': txt.replace("%", ""),
						'start': start,
						'page_len': page_len,
						'customer': filters.get('customer')
					})
