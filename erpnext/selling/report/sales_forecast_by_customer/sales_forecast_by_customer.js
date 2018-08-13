// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Sales Forecast By Customer"] = {
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
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 1,
			"width": "120px"
		},
		{
			"fieldname":"sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Int",
			"reqd": 1,
			"width": "60px"
		},
	],
	onload: function(report) {
		// dropdown for links to other reports
		report.page.add_inner_button(__("By Item"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Sales Forecast By Item', {company: filters.company, business_unit: filters.business_unit, year: filters.year});
		}, __('View'));
	}
}
