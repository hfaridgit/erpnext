// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Workstation", {
	onload: function(frm) {
		if(frm.is_new())
		{
			frappe.call({
				type:"GET",
				method:"erpnext.manufacturing.doctype.workstation.workstation.get_default_holiday_list",
				callback: function(r) {
					if(!r.exe && r.message){
						cur_frm.set_value("holiday_list", r.message);
					}
				}
			})
		}
	}, 
	refresh: function(frm) {
		frm.toggle_enable(['hour_rate_electricity', 'hour_rate_water', 'hour_rate_gas'], false);
	}
});
cur_frm.add_fetch("employee","employee_name","employee_name");
cur_frm.fields_dict['cost_center'].get_query = function(doc, cdt, cdn) {
	return {
		filters: {
			company: cur_frm.doc.company, 
			business_unit: cur_frm.doc.business_unit, 
			is_group: 0
		}
	};
}
cur_frm.fields_dict['labours'].grid.get_field("employee").get_query = function(doc, cdt, cdn) {
	return {
		filters: {
			company: cur_frm.doc.company, 
			business_unit: cur_frm.doc.business_unit
		}
	};
}
