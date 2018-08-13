// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Social Insurance Sheet"] = {
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
			"fieldname":"mm",
			"label": __("Month"),
			"fieldtype": "Int",
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"sst",
			"label": __("Salary Slip Type"),
			"fieldtype": "Link",
			"options": "Salary Slip Type",
			"reqd": 1,
			"width": "120px"
		},
		{
			"fieldname":"docst",
			"label": __("Submitted"),
			"fieldtype": "Select",
			"options": [0,1],
			"default": 0,
			"reqd": 1,
		},
	],
	"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (dataContext['كودالموظف']=='الإجمالى العام') {
			value = "<span style='color:black;'>" + value + "</span>";
			var $value = $(value).css({"display":"block","width":"100%","background-color": "#FD8692"});
			value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	}
}
