frappe.pages['organization-chart'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Organization Chart',
		single_column: true
	});
}