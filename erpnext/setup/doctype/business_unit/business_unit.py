# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class BusinessUnit(Document):
	pass

def validate_bu(ref_doc):
	if ref_doc.business_unit:
		bu = frappe.db.sql("""select if(concat(%s, %s) in (select concat(name,company) from `tabBusiness Unit`), 1, 0)
							""", (ref_doc.business_unit,ref_doc.company))
		if bu[0][0] == 0:
			frappe.throw(_("Business Unit is not correct for this Company."))

	bux = frappe.db.sql("""select concat(name,company) as kk from `tabBusiness Unit`""", as_dict=1)
	
	rows = None
			
	if ref_doc.doctype in ("Material Request", "Purchase Order", "Purchase Invoice", "Purchase Receipt", "Request for Quotation", "Supplier Quotation"):
		rows = ref_doc.items
	if ref_doc.doctype in ("Journal Entry"):
		rows = ref_doc.accounts
	if rows:
		for d in rows:
			k = "%s%s" % (d.business_unit, ref_doc.company)
			i = 0
			for b in bux:
				if b.kk == k:
					i = 1
			if i == 0:
				frappe.throw(_("Row {0}: Business Unit is not correct for this Company.").format(d.idx))
	return
	