// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Time Log', {
	refresh: function(frm) {

	}, 
	production_order: function(frm) {
		frappe.call({
			doc: frm.doc,
			method: "get_operations",
			callback: function(r) {
				if(r.message) {
					set_field_options("operation", r.message);
					refresh_field("operation");
				}
			}
		});
	},
});
cur_frm.fields_dict['production_order'].get_query = function(doc) {
	return {filters: [
						['Production Order', 'docstatus', '=', 1],
						['Production Order', 'status', 'in',['Not Started', 'In Process', 'Submitted']]
					]
	}
}