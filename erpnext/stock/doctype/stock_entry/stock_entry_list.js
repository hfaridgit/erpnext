frappe.listview_settings['Stock Entry'] = {
	refresh: function(listview) {
		if(frappe.user.has_role('Manufacture Only')) {
			if (listview.filter_list.filter_exists('Stock Entry', 'purpose', 'like', '%Manufacture%')) {
				return;
			} else {
				listview.filter_list.add_filter('Stock Entry', 'purpose', 'like', '%Manufacture%');
			}
		}
		if(frappe.user.has_role('All Except Manufacture')) {
			if (listview.filter_list.filter_exists('Stock Entry', 'purpose', 'not like', '%Manufacture%')) {
				return;
			} else {
				listview.filter_list.add_filter('Stock Entry', 'purpose', 'not like', '%Manufacture%');
			}
		}
			//frappe.route_options = {
			//	"purpose": ["=", 'Manufacture']
			//};
	},
	add_fields: ["`tabStock Entry`.`from_warehouse`", "`tabStock Entry`.`to_warehouse`",
		"`tabStock Entry`.`purpose`", "`tabStock Entry`.`production_order`", "`tabStock Entry`.`bom_no`"],
	column_render: {
		"from_warehouse": function(doc) {
			var html = "";
			if(doc.from_warehouse) {
				html += '<span class="filterable h6"\
					data-filter="from_warehouse,=,'+doc.from_warehouse+'">'
						+doc.from_warehouse+' </span>';
			}
			// if(doc.from_warehouse || doc.to_warehouse) {
			// 	html += '<i class="fa fa-arrow-right text-muted"></i> ';
			// }
			if(doc.to_warehouse) {
				html += '<span class="filterable h6"\
				data-filter="to_warehouse,=,'+doc.to_warehouse+'">'+doc.to_warehouse+'</span>';
			}
			return html;
		}
	}
};
