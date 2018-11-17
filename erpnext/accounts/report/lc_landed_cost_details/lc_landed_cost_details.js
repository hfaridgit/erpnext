// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["LC Landed Cost Details"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"business_unit",
			"label": __("business_unit"),
			"fieldtype": "Link",
			"options": "Business Unit",
			"get_query": function() {
				var company = frappe.query_report_filters_by_name.company.get_value();
				return {
					"doctype": "Business Unit",
					"filters": {
						"company": company,
					}
				}
			},
			"reqd": 1
		},
		{
			"fieldname":"project",
			"label": __("Letter Of Credit"),
			"fieldtype": "Link",
			"options": "Project",
			"get_query": function() {
				var company = frappe.query_report_filters_by_name.company.get_value();
				return {
					"doctype": "Project",
					"filters": {
						"company": company,
						"project_type": "Import Operation"
					}
				}
			},
			"reqd": 1
		},
	]
}
