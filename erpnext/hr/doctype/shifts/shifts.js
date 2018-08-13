// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shifts', {
	apply_flexible_hours: function(frm) {
		if(frm.doc.apply_flexible_hours==1) {
			frm.doc.ignore_lateness = 1;
			refresh_field("ignore_lateness");
		}
	}
});
