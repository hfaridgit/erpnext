﻿// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Forecast Monthly Materials Requirement"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1,
			on_change: function() {
					frappe.query_report_filters_by_name.business_unit.set_value("");
			}
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
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Int",
			"reqd": 1,
			"width": "60px"
		},
	],
}
