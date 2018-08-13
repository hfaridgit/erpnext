// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.provide('erpnext.selling');

erpnext.selling.SalesForecast = frappe.ui.form.Controller.extend({
	setup: function() {
		this.frm.set_query('item_code', function() {
			return {
				query: 'erpnext.controllers.queries.item_query',
				filters:{ 'is_stock_item': 1 }
			}
		});
	},

	refresh: function() {
		this.make_production_order();
	},

	make_production_order: function() {
		var me = this;

		frappe.call({
			method: 'erpnext.selling.doctype.sample_request.sample_request.has_enough_qty',
			args: { doc: me.frm.doc },
			callback: function(r) {
				if (!r) return;

				if (me.frm.doc.docstatus === 1) {
					me.frm.add_custom_button(
						frappe._('Production Order'),
						function() {
							if (r.exe) return;

							if (r.message) {
								frappe.msgprint(frappe._('Already have enough quantity'));
								return;
							}

							frappe.model.open_mapped_doc({
								method: 'erpnext.selling.doctype.sample_request.sample_request.make_production_order',
								frm: me.frm
							});
						},
						frappe._('Make')
					);
				}
			}
		});
	}
});

$.extend(cur_frm.cscript, new erpnext.selling.SalesForecast({frm: cur_frm}));

cur_frm.add_fetch('customer', 'customer_name', 'customer_name');
cur_frm.add_fetch('item_code', 'item_name', 'item_name');
