// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Punishment Rule', {
	validate: function(frm) {
		if(frm.doc.details.length<1) {
			frappe.throw(__("You Should enter at least one line of details !!"));
		}
		for (var j = 0; j < frm.doc.details.length; j++) {
			if(!frm.doc.details[j].rate && !frm.doc.details[j].action) {
				frm.get_field("details").grid.grid_rows[j].remove();
			}
		}
		refresh_field("details");
	}, 
	months_to_reset_counter: function(frm) {
		var i = frm.doc.months_to_reset_counter;
		if(i==5 || i==7 || i==8 || i==9 || i==10 || i==11 || i>12) {
			frappe.msgprint(__("Only 0, 1, 2, 3, 4, 6, 12 could be defined for reseting the counter, 0 for not to reset it."));
			frm.doc.months_to_reset_counter = 6;
			refresh_field("months_to_reset_counter");
		}
	},
});
