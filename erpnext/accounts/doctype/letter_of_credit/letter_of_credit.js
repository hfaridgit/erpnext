// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Letter of Credit', {
	refresh: function(frm) {

		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Operation Statement'), function() {
				frappe.route_options = {
					project: frm.doc.project
				};
				frappe.set_route("query-report", "Operation Statement");
			}, __("View"));
			frm.add_custom_button(__('Operation General Ledger'), function() {
				frappe.route_options = {
					project: frm.doc.project
				};
				frappe.set_route("query-report", "Operation General Ledger");
			}, __("View"));
			frm.add_custom_button(__('Landed Cost Details'), function() {
				frappe.route_options = {
					project: frm.doc.name, 
					company: frm.doc.company
				};
				frappe.set_route("query-report", "LC Landed Cost Details");
			}, __("View"));
		}
		if(frm.doc.docstatus == 1 && frm.doc.status=="Active") {
			frm.add_custom_button(__('Close'), function() {
				frappe.prompt([{fieldname:'posting_date', fieldtype: 'Date', label: 'Posting Date', reqd: 1}, 
					{fieldname:'cost_center', fieldtype: 'Link', options: 'Cost Center', label: 'Cost Center', reqd: 1, 
					get_query: function() {	return {"doctype": "Cost Center","filters": {"company": cur_frm.doc.company}}}}], 
					function(data) {
						frappe.call({
							doc: cur_frm.doc,
							method: "make_journal_entry",
							args: {
								posting_date: data.posting_date, 
								cost_center: data.cost_center
							},
							callback: (r) => {
								cur_frm.set_value("status","Closed");
								cur_frm.set_value("closing_date",data.posting_date);
								cur_frm.save("Update");
							}
						});
				}, __("Closing Date"));
			});
		}
		if(frm.doc.docstatus == 1 && frm.doc.status=="Active") {
			frm.add_custom_button(__('Purchase Invoice'), function() {
				var bgt = frappe.model.get_new_doc('Purchase Invoice');
				bgt.project = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			frm.add_custom_button(__('Purchase Receipt'), function() {
				var bgt = frappe.model.get_new_doc('Purchase Receipt');
				bgt.project = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
			frm.add_custom_button(__('Journal Entry'), function() {
				var bgt = frappe.model.get_new_doc('Journal Entry');
				bgt.project = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
			frm.add_custom_button(__('Payment Entry'), function() {
				var bgt = frappe.model.get_new_doc('Payment Entry');
				bgt.project = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
			frm.add_custom_button(__('Landed Cost Voucher'), function() {
				var bgt = frappe.model.get_new_doc('Landed Cost Voucher');
				bgt.project = frm.doc.name;
				bgt.company = frm.doc.company;
				frappe.set_route('Form', bgt.doctype, bgt.name);
			}, __("Make"));
		}
	}
});
