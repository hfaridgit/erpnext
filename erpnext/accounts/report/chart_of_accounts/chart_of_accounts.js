// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Chart Of Accounts"] = {
		"filters": [
			{
				"fieldname": "company",
				"label": __("Company"),
				"fieldtype": "Link",
				"options": "Company",
				"default": frappe.defaults.get_user_default("Company"),
				"reqd": 1
			}
		],
		"formatter": function(row, cell, value, columnDef, dataContext, default_formatter) {
			if (columnDef.df.fieldname=="account") {
				value = dataContext.account;

				columnDef.df.is_tree = true;
			}

			value = default_formatter(row, cell, value, columnDef, dataContext);

			if (!dataContext.parent_account) {
				var $value = $(value).css("font-weight", "bold");

				value = $value.wrap("<p></p>").parent().html();
			}

			return value;
		},
		"tree": true,
		"name_field": "account",
		"parent_field": "parent_account",
		"initial_depth": 1
};

