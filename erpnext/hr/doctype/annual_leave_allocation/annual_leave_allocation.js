// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Annual Leave Allocation', {
	validate: function(frm) {
		frm.doc.from_date = frappe.datetime.str_to_obj(frm.doc.from_date).getFullYear() + '-01-01';
		frm.doc.to_date = frappe.datetime.str_to_obj(frm.doc.from_date).getFullYear() + '-12-31';
	}
});
