# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document

class EmployeeLeaveApprover(Document):
	pass

def get_approvers(doctype, txt, searchfield, start, page_len, filters):
	return get_approver_listx(filters.get("user"))
		

def get_approver_list(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select user.name, user.first_name, user.last_name from
		tabUser user, `tabHas Role` user_role where
		user_role.role = "Leave Approver"
		and user_role.parent = user.name and user.enabled and
		user.name != %(name)s and 
		(user.name like %(txt)s or user.first_name like %(txt)s or user.last_name like %(txt)s)
		limit %(start)s, %(page_len)s""", 
		{
			'txt': "%%%s%%" % txt,
			'start': start,
			'page_len': page_len,
			'name': filters.get('user')
		})

def get_approver_listx(name):
	return frappe.db.sql("""select user.name, user.first_name, user.last_name from
		tabUser user, `tabHas Role` user_role where
		user_role.role = "Leave Approver"
		and user_role.parent = user.name and user.enabled and
		user.name != %s 
		""", name or "")
