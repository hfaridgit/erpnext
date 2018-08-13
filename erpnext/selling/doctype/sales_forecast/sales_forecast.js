// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.provide('erpnext.selling');

erpnext.selling.SalesForecast = frappe.ui.form.Controller.extend({
	onload: function() {
		this.set_sales_person();
		this.set_customer_query();
	},

	company: function() {
		this.set_months();
	},

	business_unit: function() {
		this.set_months();
	},

	year: function() {
		this.set_months();
	},

	customer: function() {
		this.set_months();
	},

	item_code: function() {
		this.set_uom();
		this.set_months();
	},

	set_sales_person: function() {
		var me = this;
		if (!me.frm.doc.__islocal) return;

		frappe.call({
			method: 'erpnext.selling.doctype.sales_forecast.sales_forecast.get_sales_person',
			freeze: true,
			callback: function(r) {
				if (!r) {
					frappe.throw(frappe._('Sales Person not found'));
					return;
				}

				me.frm.set_value('sales_person', r.message);
			}
		});
	},

	set_customer_query: function() {
		var me = this;

		me.frm.set_query('customer', function() {
			return {
				query: 'erpnext.selling.doctype.sales_forecast.sales_forecast.customer_query'
			};
		});
	},

	set_uom: function() {
		var me = this;

		if (!me.frm.doc.item_code) {
			me.frm.set_value('uom', null);
			return;
		}

		frappe.db.get_value('Item', me.frm.doc.item_code, 'stock_uom', function(r) {
			if (!r) return;
			me.frm.set_value('uom', r.stock_uom);
		});
	},

	set_months: function() {
		var me = this;

		if (
			!me.frm.doc.company ||
			!me.frm.doc.business_unit ||
			!me.frm.doc.year ||
			!me.frm.doc.customer ||
			!me.frm.doc.item_code
		) return;

		frappe.call({
			method: 'erpnext.selling.doctype.sales_forecast.sales_forecast.get_months',
			args: {doc: me.frm.doc},
			freeze: true,
			callback: function(r) {
				if (!r) return;
				me.frm.set_value('months', r.message);
			}
		});
	}
});

frappe.ui.form.on('Sales Forecast Month', {
	form_render: function(frm, cdt, cdn) {
		var doc = frappe.model.get_doc(cdt, cdn);
		var row_index = doc.idx - 1;

		var toggle_enablement = function(enabled) {
			['qty', 'rate'].forEach(function(field) {
				let $wrapper = frm.fields_dict.months.grid.grid_rows[row_index].grid_form.fields_dict[field].$wrapper;
				$wrapper.find('.control-input').toggle(enabled);
				$wrapper.find('.control-value').toggle(!enabled);
			});
		};

		toggle_enablement(false);

		frappe.call({
			method: 'erpnext.selling.doctype.sales_forecast.sales_forecast.get_month_statuses',
			args: {doc: frm.doc},
			freeze: true,
			callback: function(r) {
				if (!r) return;
				toggle_enablement(r.message[row_index]);
			}
		});
	},

	qty: function(frm, cdt, cdn) {
		var doc = frappe.model.get_doc(cdt, cdn);

		frappe.db.get_value('Item Price', {item_code: frm.doc.item_code}, 'price_list_rate', function(r) {
			if (!r) return;
			frappe.model.set_value(cdt, cdn, 'rate', r.price_list_rate);
		});
	},

	rate: function(frm, cdt, cdn) {
		var doc = frappe.model.get_doc(cdt, cdn);

		frappe.db.get_value('Item Price', {item_code: frm.doc.item_code}, 'price_list_rate', function(r) {
			if (!r) return;

			if (doc.rate < r.price_list_rate) {
				frappe.model.set_value(cdt, cdn, 'rate', r.price_list_rate);
				frappe.msgprint(frappe._('Item Price must be greater than or equal to Last Item Price'))
			}
		});
	}
});

$.extend(cur_frm.cscript, new erpnext.selling.SalesForecast({frm: cur_frm}));
cur_frm.add_fetch('customer', 'customer_name', 'customer_name');
cur_frm.add_fetch('item_code', 'item_name', 'item_name');
