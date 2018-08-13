// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Job", {
	onload: function(frm) {
		frm.list_route = "Tree/Job";

		//get query select Jobs
		frm.fields_dict['parent_job'].get_query = function(doc,cdt,cdn) {
			return{
				filters:[
					['Job', 'is_group', '=', 1],
					['Job', 'name', '!=', doc.job_name]
				]
			}
		}
	},

	refresh: function(frm) {
		frm.trigger("set_root_readonly");
		frm.add_custom_button(__("Jobs Tree"), function() {
			frappe.set_route("Tree", "Job");
		});

		if(!frm.is_new()) {
			frm.add_custom_button(__("Emloyees"), function() {
				frappe.set_route("List", "Employee", {"job_name": frm.doc.name});
			});
		}
	},

	set_root_readonly: function(frm) {
		// read-only for root jobs
		frm.set_intro("");
		if(!frm.doc.parent_job) {
			frm.set_read_only();
			frm.set_intro(__("This is a root job and cannot be edited."), true);
		}
	},

	page_name: frappe.utils.warn_page_name_change
});
