// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Time Log Tool', {
	onload: function(frm) {
		frm.toggle_display('start_btn', false);
		frm.toggle_display('end_btn', false);

	},
	refresh: function(frm) {
		frm.disable_save();

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
	operation: function(frm) {
		frappe.call({
			doc: frm.doc,
			method: "get_times",
			callback: function(r) {
				if(r.message) {
					frm.toggle_display('start_btn', r.message[0].from_time==0);
					frm.toggle_display('end_btn', r.message[0].to_time==0);
				} else {
					frm.toggle_display('start_btn', true);
					frm.toggle_display('end_btn', true);
				}
				refresh_field("start_btn");
				refresh_field("end_btn");
			}
		});
	},
	start_btn: function(frm) {
		frappe.call({
			doc: frm.doc,
			method: "register_start",
			callback: function(r) {
					frm.toggle_display('start_btn', false);
			}
		});
	},
	end_btn: function(frm) {
		frappe.call({
			doc: frm.doc,
			method: "register_end",
			callback: function(r) {
					frm.toggle_display('end_btn', false);
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