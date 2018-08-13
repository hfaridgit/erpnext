// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.provide('erpnext.selling');

erpnext.selling.SalesForecast = frappe.ui.form.Controller.extend({
	onload: function() {
		this.set_sales_person();
		this.set_customer_query();
		this.set_item_query();
	},

	customer: function() {
		this.set_items();
	},

	set_sales_person: function() {
		var me = this;
		if (!me.frm.doc.__islocal) return;

		frappe.call({
			method: 'erpnext.selling.doctype.sales_forecast.sales_forecast.get_sales_person',
			freeze: true,
			callback: function(r) {
				if (!r || !r.message) {
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

	set_item_query: function(frm, cdt, cdn, suffix) {
		var me = this;

		me.frm.set_query('item', 'items', function() {
			return {
				filters: {
					item_code: [
						'NOT IN',
						me.frm.doc.items.map(i => i.item).filter(i => i)
					]
				}
			};
		});
	},

	set_items: function() {
		var me = this;

		if (
			!me.frm.doc.company ||
			!me.frm.doc.business_unit ||
			!me.frm.doc.year ||
			!me.frm.doc.customer
		) return;

		frappe.call({
			method: 'erpnext.selling.doctype.sales_forecast.sales_forecast.get_items',
			args: {doc: me.frm.doc},
			freeze: true,
			callback: function(r) {
				if (!r || !r.message) return;
				me.frm.set_value('items', r.message);
			}
		});
	}
});

cur_frm.cscript.item_suffixes = ['_q11', '_q12', '_q13', '_q24', '_q25', '_q26', '_q37', '_q38', '_q39', '_q410', '_q411', '_q412'];

cur_frm.cscript.sales_forecast_item = {
	form_render: function(frm, cdt, cdn) {
		var doc = frappe.model.get_doc(cdt, cdn);

		['qty', 'final_price', 'choose_the_price'].forEach(function(field) {
			frm.cscript.item_suffixes.forEach(function(suffix, i) {
				var $wrapper = frm.fields_dict.items.grid.grid_rows[doc.idx - 1].grid_form.fields_dict[field + suffix].$wrapper;
				$wrapper.find('.control-input').toggle(false);
				$wrapper.find('.control-value').toggle(true);
			});
		});

		frappe.call({
			method: 'erpnext.selling.doctype.sales_forecast.sales_forecast.get_month_statuses',
			args: {doc: frm.doc},
			freeze: true,
			callback: function(r) {
				if (!r || !r.message) return;

				['qty', 'final_price', 'choose_the_price'].forEach(function(field) {
					frm.cscript.item_suffixes.forEach(function(suffix, i) {
						var $wrapper = frm.fields_dict.items.grid.grid_rows[doc.idx - 1].grid_form.fields_dict[field + suffix].$wrapper;
						$wrapper.find('.control-input').toggle(r.message[i]);
						$wrapper.find('.control-value').toggle(!r.message[i]);
					});
				});
			}
		});
	},

	item: function(frm, cdt, cdn) {
		var doc = frappe.model.get_doc(cdt, cdn);
		if (!doc.item) return;
		var item_codes = frm.doc.items.map(i => i.item);
		item_codes.pop();

		if (item_codes.indexOf(doc.item) !== -1) {
			frappe.model.set_value(cdt, cdn, 'item', null);
			frappe.msgprint(frappe._('Item already exists'));
			return;
		}

		frappe.call({
			method: 'erpnext.selling.doctype.sales_forecast.sales_forecast.get_item',
			args: {doc: frm.doc, item: doc},
			freeze: true,
			callback: function(r) {
				if (!r || !r.message) return;
				frappe.model.set_value(cdt, cdn, r.message);
			}
		});
	},

	set_price_and_rate: function(frm, cdt, cdn, suffix) {
		var doc = frappe.model.get_doc(cdt, cdn);

		frappe.call({
			method: 'erpnext.selling.doctype.sales_forecast.sales_forecast.get_item_price_and_rate',
			args: {item: doc, doc: frm.doc},
			freeze: true,
			callback: function(r) {
				if (!r || !r.message) return;
				var fields = {};
				fields['last_price_list_rate' + suffix] = r.message.base_price_list_rate;
				fields['last_sales_rate' + suffix] = r.message.base_rate;
				frappe.model.set_value(cdt, cdn, fields);
			}
		});
	},

	set_final_price: function(frm, cdt, cdn, suffix) {
		var doc = frappe.model.get_doc(cdt, cdn);
		var final_price = 0;

		switch (doc['choose_the_price' + suffix]) {
			case 'Last Price List Rate':
				final_price = doc['last_price_list_rate' + suffix];
				break;
			case 'Last Sales Rate':
				final_price = doc['last_sales_rate' + suffix];
				break;
		}

		frappe.model.set_value(cdt, cdn, 'final_price' + suffix, final_price);
	},

	toggle_final_price: function(frm, cdt, cdn, suffix) {
		var doc = frappe.model.get_doc(cdt, cdn);
		var $wrapper = frm.fields_dict.items.grid.grid_rows[doc.idx - 1].grid_form.fields_dict['final_price' + suffix].$wrapper;

		if (doc['choose_the_price' + suffix] === 'Other') {
			$wrapper.find('.control-input').toggle(true);
			$wrapper.find('.control-value').toggle(false);
		} else {
			$wrapper.find('.control-input').toggle(false);
			$wrapper.find('.control-value').toggle(true);
		}
	}
};

cur_frm.cscript.item_suffixes.forEach(function(suffix) {
	cur_frm.cscript.sales_forecast_item['qty' + suffix] = function(frm, cdt, cdn) {
		frm.cscript.sales_forecast_item.set_price_and_rate(frm, cdt, cdn, suffix);
	};

	cur_frm.cscript.sales_forecast_item['choose_the_price' + suffix] = function(frm, cdt, cdn) {
		frm.cscript.sales_forecast_item.set_final_price(frm, cdt, cdn, suffix);
	};

	cur_frm.cscript.sales_forecast_item['final_price' + suffix] = function(frm, cdt, cdn) {
		frm.cscript.sales_forecast_item.toggle_final_price(frm, cdt, cdn, suffix);
	};
});

$.extend(cur_frm.cscript, new erpnext.selling.SalesForecast({frm: cur_frm}));
frappe.ui.form.on('Sales Forecast Item', cur_frm.cscript.sales_forecast_item);
cur_frm.add_fetch('customer', 'customer_name', 'customer_name');
