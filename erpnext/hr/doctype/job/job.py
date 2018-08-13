# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet

class Job(NestedSet):
	nsm_parent_field = 'parent_job'

	def validate(self):
		self.validate_mandatory()

	def validate_mandatory(self):
		if self.job_name != self.company and not self.parent_job:
			frappe.throw(_("Please enter parent job"))
		elif self.job_name == self.company and self.parent_job:
			frappe.throw(_("Root cannot have a parent job"))

	def convert_group_to_ledger(self):
		if self.check_if_child_exists():
			frappe.throw(_("Cannot convert Job as it has child nodes"))
		else:
			self.is_group = 0
			self.save()
			return 1

	def convert_ledger_to_group(self):
		self.is_group = 1
		self.save()
		return 1

	def check_if_child_exists(self):
		return frappe.db.sql("select name from `tabJob` where \
			parent_job = %s and docstatus != 2", self.name)

	def before_rename(self, olddn, newdn, merge=False):

		# Validate properties before merging
		super(Job, self).before_rename(olddn, newdn, merge, "is_group")

		return new_job

	def after_rename(self, olddn, newdn, merge=False):
		if not merge:
			frappe.db.set_value("Job", newdn, "job_name")
		else:
			super(Job, self).after_rename(olddn, newdn, merge)

@frappe.whitelist()
def get_children(doctype, parent, company, is_root=False):
	args = frappe.local.form_dict
	#company = args['company']

	# root
	#if args['parent'] == company:
	if is_root:
		jb = frappe.db.sql("""select 
			name as value, is_group as expandable, designation 
			from `tabJob` 
			where ifnull(`parent_job`,'') = '' 
			and `company`=%s and docstatus<2 
			order by name""", company, as_dict=1)

	else:
		# other
		jb = frappe.db.sql("""select 
			name as value, is_group as expandable, parent_job as parent, designation 
			from `tabJob` 
			where ifnull(`parent_job`,'') = %s 
			and docstatus<2 
			order by name""", parent, as_dict=1)


	return jb

@frappe.whitelist()
def get_emp_data(job_name=None):
	if job_name:
		jb = frappe.db.sql("""select j.designation, e.name as reports_to from `tabJob` j
				left join `tabEmployee` e on e.job_name=j.parent_job
				where j.name=%s""", job_name, as_dict=1)

	return jb

@frappe.whitelist()
def get_org_chart(company=None):
	org_data = frappe.db.sql("""select a.*, ifnull(b.employees,0) as employees from (
									select j.lvl, j.designation, j.name as job_name 
									from (SELECT (COUNT(parent.name) - 1) as lvl, node.name AS name,node.company, node.enabled, node.lft, node.designation  
									FROM `tabJob` AS node,
											`tabJob` AS parent
									WHERE node.lft BETWEEN parent.lft AND parent.rgt
									GROUP BY node.name
									ORDER BY node.lft) j  
									where j.enabled=1 and j.company=%s
									order by j.lft) a
									left join (select job_name, count(*) as employees from `tabEmployee` 
									where status='Active' 
									group by job_name) b
									on a.job_name=b.job_name
									""" , (company), as_dict=True)
	return org_data

@frappe.whitelist()
def get_org_charthhh(company=None):
	org_data = frappe.db.sql("""select j.lvl, e.employee, e.employee_name, j.designation, e.image, j.name as job_name 
									from (SELECT (COUNT(parent.name) - 1) as lvl, node.name AS name,node.company, node.enabled, node.lft, node.designation  
									FROM `tabJob` AS node,
											`tabJob` AS parent
									WHERE node.lft BETWEEN parent.lft AND parent.rgt
									GROUP BY node.name
									ORDER BY node.lft) j  
									left join `tabEmployee` e on e.job_name=j.name and e.status<>'Left'
									where j.enabled=1 and j.company=%s
									order by j.lft""" , (company), as_dict=True)
	return org_data

