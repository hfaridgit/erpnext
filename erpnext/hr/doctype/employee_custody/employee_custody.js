// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'business_unit', 'business_unit');

frappe.ui.form.on('Employee Custody', {
	refresh: function(frm) {

	}
});
