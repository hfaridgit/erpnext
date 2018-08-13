// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Letter of Credit', {
	refresh: function(frm) {

		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					lc_no: frm.doc.name, 
					company: frm.doc.company
				};
				frappe.set_route("query-report", "LC Accounting Ledger");
			}, __("View"));
		}
		if(frm.doc.docstatus == 1 && frm.doc.status=="Active") {
			frm.add_custom_button(__('Close'), function() {
				frm.set_value("status","Closed");
				frm.save("Update");
			});
		}
		if(frm.doc.docstatus == 1 && frm.doc.status=="Active") {
			frm.add_custom_button(__('Purchase Invoice'), function() {
				var bgt = frappe.model.get_new_doc('Purchase Invoice');
				bgt.lc_no = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			frm.add_custom_button(__('Purchase Receipt'), function() {
				var bgt = frappe.model.get_new_doc('Purchase Receipt');
				bgt.lc_no = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
			frm.add_custom_button(__('Journal Entry'), function() {
				var bgt = frappe.model.get_new_doc('Journal Entry');
				bgt.lc_no = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
			frm.add_custom_button(__('Payment Entry'), function() {
				var bgt = frappe.model.get_new_doc('Payment Entry');
				bgt.lc_no = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
			frm.add_custom_button(__('Landed Cost Voucher'), function() {
				var bgt = frappe.model.get_new_doc('Landed Cost Voucher');
				bgt.lc_no = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
		}
	}
});
