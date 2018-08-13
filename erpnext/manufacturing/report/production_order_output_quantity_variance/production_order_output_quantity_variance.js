// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Production Order Output Quantity Variance"] = {
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
			"label": __("Business Unit"),
			"fieldtype": "Link",
			"options": "Business Unit",
			"reqd": 1
		},
		{
			"fieldname":"production_order",
			"label": __("Production Order"),
			"fieldtype": "Link",
			"options": "Production Order",
			"get_query": function() {
				var company = frappe.query_report_filters_by_name.company.get_value();
				var bu = frappe.query_report_filters_by_name.business_unit.get_value();
				return {
					"doctype": "Production Order",
					"filters": {
						"company": company,
						"business_unit": bu,
					}
				}
			},
			"reqd": 1
		},
	]
}
