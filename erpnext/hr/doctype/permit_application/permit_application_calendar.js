// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["Permit Application"] = {
	field_map: {
		"start": "permit_date",
		"end": "permit_date",
		"id": "name",
		"title": "employee_name",
		"status": "status",
		"allDay": "allDay"
	},
	options: {
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month'
		}
	},
	get_events_method: "erpnext.hr.doctype.permit_application.permit_application.get_events"
}