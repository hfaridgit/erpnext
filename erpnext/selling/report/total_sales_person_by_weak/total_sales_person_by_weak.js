// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Total Sales Person by Weak"] = {
	"filters": [
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Int",
			"default": frappe.sys_defaults.fiscal_year,
			"reqd": 1
		},
		{
			"fieldname":"week",
			"label": __("Week"),
			"fieldtype": "Int"
		},
		{
			"fieldname":"sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person"
		}
	]
}
