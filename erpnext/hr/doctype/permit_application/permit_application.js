// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee','employee_name','employee_name');
cur_frm.add_fetch('employee','company','company');

frappe.ui.form.on("Permit Application", {
	onload: function(frm) {
		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", frappe.datetime.get_today());
		}

		frm.set_query("leave_approver", function() {
			return {
				query: "erpnext.hr.doctype.permit_application.permit_application.get_approvers",
				filters: {
					employee: frm.doc.employee
				}
			};
		});

		frm.set_query("employee", erpnext.queries.employee);

	},

	refresh: function(frm) {
		if (frm.is_new()) {
			frm.set_value("status", "Open");
		}
	},

	leave_approver: function(frm) {
		if(frm.doc.leave_approver){
			frm.set_value("leave_approver_name", frappe.user.full_name(frm.doc.leave_approver));
		}
	},

	employee: function(frm) {
		frm.trigger("get_permit_balance");
	},

	get_permit_balance: function(frm) {
		if(frm.doc.docstatus==0 && frm.doc.employee && frm.doc.total_units && frm.doc.permit_date) {
			return frappe.call({
				method: "erpnext.hr.doctype.permit_application.permit_application.get_permit_balance_on",
				args: {
					employee: frm.doc.employee,
					date: frm.doc.permit_date
				},
				callback: function(r) {
					if (!r.exc && r.message) {
						frm.set_value('permit_balance', r.message);
					}
				}
			});
		}
	},

});
