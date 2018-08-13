frappe.treeview_settings["Job"] = {
	//breadcrumbs: "HR",
	//title: __("Organization Chart"),
	get_tree_root: false,
	filters: [{
		fieldname: "company",
		fieldtype:"Select",
		options: $.map(locals[':Company'], function(c) { return c.name; }).sort(),
		label: __("Company"),
		default: frappe.defaults.get_default('company') ? frappe.defaults.get_default('company'): ""
	}],
	//root_label: "Jobs",
	get_tree_nodes: 'erpnext.hr.doctype.job.job.get_children',
	fields: [
		{fieldtype:'Data', fieldname:'job_name', label:__('New Job Code'), reqd:true,
			description: __("Job Code. Note: Each Job must have a unique code")},
		{fieldtype:'Check', fieldname:'is_group', label:__('Is Group'),
			description: __('Further jobs can be made under Groups, to build the organization hierarchy.')},
		{fieldtype:'Link', fieldname:'designation', label:__('Designation'), options:"Designation", reqd:true,
			description: __("Choose the right Designation for this job.")}
	],
	ignore_fields:["parent_job"],
	onload: function(treeview) {
		// Organization Chart
		function get_company() {
			return treeview.page.fields_dict.company.get_value();
		}
		treeview.page.add_inner_button(__("Organization Chart"), function() {
			hhh = frappe.call({
				method:"erpnext.hr.doctype.job.job.get_org_chart",
				args:{
					company: get_company(),
				},
				callback: function(r) {
					if (r.message) {
						localStorage.setItem('myObject', JSON.stringify(r.message));
						 window.open(frappe.urllib.get_base_url()+"/assets/js/org_chart.html",'_blank');
					}
				}
			});
			//window.open(frappe.urllib.get_base_url()+"/assets/js/org_chart.html",'_blank');
		}, __('View'));
	},
	onrender: function(node) {
		var dsc = node.data.designation;
		if (node.data && node.data.designation!==undefined) {
			$('<span class="balance-area text-muted small">    ( ' +
				 node.data.designation + ' )  </span>').insertBefore(node.$ul);
		}
	},
}
