
//frappe.provide("frappe.bus_attendance");

frappe.pages['bus_attendance'].on_page_load = function(wrapper) {
	var me = this;
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Bus Attendance'),
		single_column: true
	});

	frappe.breadcrumbs.add("HR");
	 window.check_type = 0;
	//frappe.call({
	//	"method": "erpnext.hr.page.bus_attendance.bus_attendance.get_attendance_details",
	//	callback: function (r) {
	//		var data = r.message;
	//		me.page.main.html(frappe.render_template("bus_attendance", {data: data}));
	//	}
	//});

};

frappe.pages['bus_attendance'].refresh = function() {
	var me = this;
	frappe.call({
		"method": "erpnext.hr.page.bus_attendance.bus_attendance.get_attendance_details",
		callback: function (r) {
			var data = r.message;
			me.page.main.html(frappe.render_template("bus_attendance", {data: data}));
		}
	});
};

frappe.pages['bus_attendance'].check = function(rn, ct) {
	var me = this;
	frappe.call({
		"method": "erpnext.hr.page.bus_attendance.bus_attendance.check",
		args: {
			route_name: $(rn).attr('data-name'), 
			check_type: ct
		}, 
		callback: function (r) {
			frappe.pages['bus_attendance'].refresh();
			frappe.utils.play_sound("submit");
		}
	});
};

