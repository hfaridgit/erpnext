frappe.pages['customers_map_view'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Customers Locations',
		single_column: true
	});
	page.add_inner_button(__("Go To Map"), function() {
		//window.location = "/assets/js/customers_map_view.html";
		window.open(frappe.urllib.get_base_url()+"/assets/js/customers_map_view.html",'_blank');
	});

	frappe.breadcrumbs.add("Selling");
//	frappe.require("http://maps.google.com/maps/api/js")
	hhh = frappe.call({
		method:"frappe.client.get_list",
		args:{
			doctype: "Customer",
			filters: [
				["is_frozen","=", 0]
			],
			fields: ["customer_name", "latitude", "longitude"]
		},
		callback: function(r) {
			if (r.message) {
				localStorage.setItem('mapObject', JSON.stringify(r.message));
				 window.open(frappe.urllib.get_base_url()+"/assets/js/customers_map_view.html",'_blank');
				//window.location.assign("/assets/js/customers_map_view.html");
				//msgprint(window.positions[0].customer_name);
				//alert(window.positions[0].title);
				//$(frappe.render_template('customers_map_view', {positions:r.message || []})).appendTo(page.body);
				//$(frappe.render_template("customers_map_view")).appendTo(page.body.addClass("no-border"));
				//e.target.awesomplete.list = r.message.map(function(d) { return d.attribute_value; });
			}
		}
	});

};
