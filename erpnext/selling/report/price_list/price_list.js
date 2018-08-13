// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Price List"] = {
	"filters": [
		{
			"fieldname":"price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
			"reqd": 1,
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"reqd": 1,
		},
		{
			"fieldname":"currency",
			"label": __("Currency"),
			"fieldtype": "Link",
			"default": "EGP",
			"options": "Currency",
			"reqd": 1,
		},
	]
}
