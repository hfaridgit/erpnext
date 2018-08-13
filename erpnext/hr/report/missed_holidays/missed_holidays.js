// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Missed Holidays"] = {
	"filters": [
		{
			"fieldname":"holiday_list",
			"label": __("Holiday List"),
			"fieldtype": "Link",
			"options": "Holiday List",
			"reqd": 1
		},
		{
			"fieldname":"holiday_name",
			"label": __("Holiday Name"),
			"fieldtype": "Link",
			"options": "Holiday Name",
			"reqd": 1
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Data",
			"reqd": 1
		}
	]
}
