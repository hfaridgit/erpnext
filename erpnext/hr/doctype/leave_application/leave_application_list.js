frappe.listview_settings['Leave Application'] = {
	add_fields: ["status", "leave_type", "employee", "employee_name", "total_leave_days", "from_date", "to_date"],
	filters:[["status","!=", "Rejected"]],
	get_indicator: function(doc) {
		return [__(doc.status), frappe.utils.guess_colour(doc.status),
			"status,=," + doc.status];
	},
	onload: function (listview) {
		//var me = this;

		//bulk assignment
		var method = "frappe.direction.customizations.approve_multiple";

		listview.page.add_menu_item(__("Approve"), function () {
			var docnames = listview.get_checked_items().map(function (doc) {
				return doc.name;
			});

			if (docnames.length >= 1) {
				listview.call_for_selected_items(method, { "doctype": listview.doctype, "status": "Approved" });
			}
			else {
				frappe.msgprint(__('Select records to Approve'))
			}
		});
		listview.page.add_menu_item(__("Reject"), function () {
			var docnames = listview.get_checked_items().map(function (doc) {
				return doc.name;
			});

			if (docnames.length >= 1) {
				listview.call_for_selected_items(method, { "doctype": listview.doctype, "status": "Rejected" });
			}
			else {
				frappe.msgprint(__('Select records to Reject'))
			}
		});
		listview.page.add_menu_item(__('Submit'), function () {

			var docnames = listview.get_checked_items().map(function (doc) {
				return doc.name;
			});

			if (docnames.length >= 1) {
				frappe.call({
					method: 'frappe.direction.customizations.submit_multiple',
					freeze: true,
					args: {
						items: docnames,
						doctype: listview.doctype
					},
					callback: function () {
						listview.$page.find('.list-select-all').prop('checked', false);
						frappe.utils.play_sound('submit');
						listview.refresh(true);
					}
				})
			}
			else {
				frappe.msgprint(__('Select records for submit'))
			}
		});

	},

};
