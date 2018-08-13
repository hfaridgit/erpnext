// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Transactions Tool', {
	refresh: function(frm) {
		if(frm.doc.docstatus==1 && frm.doc.submitted==1) {
			frm.add_custom_button(__('Re-Open'), function () {
				return frappe.call({
					doc: cur_frm.doc,
					method: 'reopen_month_transactions',
					freeze: true,
					freeze_message: __("Openning ... Please Wait."),
					callback: function() {
						cur_frm.reload_doc();
					}
				});
				//$c('runserverobj', { 'method': 'generate_month_transactions', 'docs': cur_frm.doc }, function (r, rt) {});
			});
		}
		if(frm.doc.docstatus==1 && frm.doc.submitted==0) {
			frm.add_custom_button(__('Generate Transactions'), function () {
				return frappe.call({
					doc: cur_frm.doc,
					method: 'generate_month_transactions',
					freeze: true,
					freeze_message: __("Generating ... Please Wait."),
					callback: function() {
					}
				});
				//$c('runserverobj', { 'method': 'generate_month_transactions', 'docs': cur_frm.doc }, function (r, rt) {});
			});
			frm.add_custom_button(__('Re-Generate Transactions'), function () {
				return frappe.call({
					doc: cur_frm.doc,
					method: 'regenerate_month_transactions',
					freeze: true,
					freeze_message: __("Re-Generating ... Please Wait."),
					callback: function() {
					}
				});
				//$c('runserverobj', { 'method': 'regenerate_month_transactions', 'docs': cur_frm.doc }, function (r, rt) {});
			});
			if(frm.doc.last_generate_date) {
				frm.add_custom_button(__('Update Generated Transactions'), function () {
					return frappe.call({
						doc: cur_frm.doc,
						method: 'update_generated_transactions',
						freeze: true,
						freeze_message: __("Updating ... Please Wait."),
						callback: function() {
						}
					});
					//$c('runserverobj', { 'method': 'regenerate_month_transactions', 'docs': cur_frm.doc }, function (r, rt) {});
				});
			}
			frm.add_custom_button(__('Delete Transactions'), function () {
				frappe.confirm(__("Do you really want to Delete Transactions?"), function () {
					return frappe.call({
						doc: cur_frm.doc,
						method: 'delete_month_transactions',
						freeze: true,
						freeze_message: __("Deleting ... Please Wait."),
						callback: function() {
						}
					});
					//$c('runserverobj', { 'method': 'delete_month_transactions', 'docs': cur_frm.doc }, function (r, rt) {});
				});
			});
			frm.add_custom_button(__('Submit Transactions'), function () {
				frappe.confirm(__("Do you really want to Submit Transactions?"), function () {
					return frappe.call({
						doc: cur_frm.doc,
						method: 'submit_month_transactions',
						freeze: true,
						freeze_message: __("Submitting ... Please Wait."),
						callback: function() {
							cur_frm.reload_doc();
						}
					});
					//$c('runserverobj', { 'method': 'submit_month_transactions', 'docs': cur_frm.doc }, function (r, rt) {});
				});
			});
		}
	}, 
	validate: function(frm) {
		if(frm.doc.transaction_year>2099 || frm.doc.transaction_year<2000) {
			frappe.throw(__("Wrong Year Entered."));
		}
		if(frm.doc.transaction_month>12 || frm.doc.transaction_month<1) {
			frappe.throw(__("Wrong Month Entered."));
		}
	}
});
