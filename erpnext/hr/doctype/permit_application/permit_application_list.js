frappe.listview_settings['Permit Application'] = {
	add_fields: ["status", "employee", "employee_name", "total_units", "permit_date"],
	filters:[["status","!=", "Rejected"]],
	get_indicator: function(doc) {
		return [__(doc.status), frappe.utils.guess_colour(doc.status),
			"status,=," + doc.status];
	}
};
