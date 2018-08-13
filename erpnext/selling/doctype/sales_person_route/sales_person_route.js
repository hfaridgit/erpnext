// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Person Route', {
	setup: function(frm){
		frm.fields_dict["invoices"].grid.get_field("sales_invoice").get_query = function(doc, cdt, cdn){
			return{
				query: "erpnext.selling.doctype.sales_person_route.sales_person_route.invoice_query",
				filters: {'customer': doc.customer}
			}
		}
	}, 
	onload: function(frm) {
		frm.set_query('customer', function() {
			return {
				query: 'erpnext.selling.doctype.sales_person_route.sales_person_route.customer_query'
			};
		});
		if (!frm.doc.__islocal) return;

		frappe.call({
			method: 'erpnext.selling.doctype.sales_person_route.sales_person_route.get_sales_person',
			freeze: true,
			callback: function(r) { 
				if (!r) {
					frappe.throw(frappe._('Sales Person not found'));
					return;
				}

				frm.set_value('sales_person', r.message);
			}
		});
	},
	
});
