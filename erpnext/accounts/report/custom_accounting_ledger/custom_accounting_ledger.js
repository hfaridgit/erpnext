// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Custom Accounting Ledger"] = {
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
			"fieldname":"against_voucher_type",
			"label": __("Against Voucher Type"),
			"fieldtype": "Link",
			"options": "DocType",
			"reqd": 1
		},
		{
			"fieldname":"against_voucher",
			"label": __("Against Voucher No"),
			"fieldtype": "Data",
			"reqd": 1
		},
	]
}
