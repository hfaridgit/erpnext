// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt



cur_frm.cscript.onload = function(doc) {
	cur_frm.set_value("company", frappe.defaults.get_user_default("Company"))
}

cur_frm.cscript.refresh = function(doc) {
	cur_frm.disable_save();
}

cur_frm.add_fetch("production_order", "planned_start_date", "planned_start_date");
cur_frm.add_fetch("production_order", "production_item", "production_item");
cur_frm.add_fetch("production_order", "bom_no", "bom_no");
cur_frm.add_fetch("production_order", "description", "description");
cur_frm.add_fetch("production_order", "qty", "pending_qty");
cur_frm.add_fetch("production_order", "fg_warehouse", "warehouse");
cur_frm.add_fetch("production_item", "stock_uom", "stock_uom");
cur_frm.add_fetch("item_code", "stock_uom", "stock_uom");
cur_frm.add_fetch("item_code", "description", "description");

frappe.ui.form.on("Materials Planning Tool", {
	onload_post_render: function(frm) {
		frm.get_field("items").grid.set_multiple_add("item_code", "warehouse", "pending_qty");
	},
	get_production_orders: function(frm) {
		if(!frm.doc.company || !frm.doc.business_unit) {
			frappe.throw(__("Company and Business Unit are Mandatory."));
		}
		frappe.call({
			doc: frm.doc,
			method: "get_open_production_orders",
			callback: function(r) {
				refresh_field("production_orders");
			}
		});
	},
	
	get_items: function(frm) {
		frappe.call({
			doc: frm.doc,
			method: "get_po_items",
			callback: function(r) {
				refresh_field("items");
			}
		});
	},
	
	create_material_requests: function(frm) {
		if(!frm.doc.requested_by_date) {
			frappe.throw(__("Please enter the Requested by Date for Materials."));
		}
		frappe.call({
			doc: frm.doc,
			method: "raise_material_requests"
		});
	}
});

cur_frm.cscript.item_code = function(doc,cdt,cdn) {
	var d = locals[cdt][cdn];
	if (d.item_code) {
		frappe.call({
			method: "erpnext.manufacturing.doctype.materials_planning_tool.materials_planning_tool.get_item_details",
			args: {
				"item" : d.item_code
			},
			callback: function(r) {
				$.extend(d, r.message);
				refresh_field("items");
			}
		});
	}
}

cur_frm.fields_dict['production_orders'].grid.get_field('production_order').get_query = function(doc) {
	return {filters: [
						['Production Order', 'docstatus', '=', 1],
						['Production Order', 'status', 'in',['Not Started', 'In Process', 'Submitted']],
						['Production Order', 'company', '=', cur_frm.doc.company], 
						['Production Order', 'business_unit', '=', cur_frm.doc.business_unit]
					]
	}
}

cur_frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc) {
	return erpnext.queries.item({
		'is_stock_item': 1
	});
}

