
//frappe.provide("frappe.customer_geo");

frappe.pages['customer_geo'].on_page_load = function(wrapper) {
	var me = this;
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Customer Geo'),
		single_column: true
	});

	frappe.breadcrumbs.add("Selling");
	 //window.check_type = 0;
};

frappe.pages['customer_geo'].refresh = function() {
	var me = this;
	frappe.call({
		"method": "erpnext.selling.page.customer_geo.customer_geo.get_location_details",
		callback: function (r) {
			if (r.message) {
				var data = r.message;
				me.page.main.html(frappe.render_template("customer_geo", {data: data}));
			} else  {
				frappe.msgprint(__("No Customers Defined for You."));
			}
		}
	});
};

frappe.pages['customer_geo'].check = function(rn, ct) {
	var me = this;
	$.getJSON('http://ip-api.com/json', function (data, status) {
	//alert($(rn).attr('data-name'));
        if(status === "success") {
            if(data.lat && data.lon) {
                //if there's not zip code but we have a latitude and longitude, let's use them
				frappe.call({
					"method": "erpnext.selling.page.customer_geo.customer_geo.check",
					args: {
						customer: $(rn).attr('data-name'),
						latitude: data.lat,
						longitude: data.lon
					}, 
					callback: function (r) {
						frappe.pages['customer_geo'].refresh();
						frappe.utils.play_sound("submit");
					}
				});
            } else {
                    //if there's an error 
                    locationOnError();
            }
        } else {
            locationOnError();
        }
    });
};

