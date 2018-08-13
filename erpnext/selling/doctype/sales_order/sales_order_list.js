frappe.listview_settings['Sales Order'] = {
	add_fields: ["base_grand_total", "customer_name", "currency", "delivery_date",
		"per_delivered", "per_billed", "status", "order_type", "name"],
	get_indicator: function(doc) {
		if(doc.status==="Closed"){
			return [__("Closed"), "green", "status,=,Closed"];

		} else if (doc.order_type !== "Maintenance"
			&& flt(doc.per_delivered, 6) < 100 && frappe.datetime.get_diff(doc.delivery_date) < 0) {
			// to bill & overdue
			return [__("Overdue"), "red", "per_delivered,<,100|delivery_date,<,Today|status,!=,Closed"];

		} else if (doc.order_type !== "Maintenance"
			&& flt(doc.per_delivered, 6) < 100 && doc.status!=="Closed") {
			// not delivered

			if(flt(doc.per_billed, 6) < 100) {
				// not delivered & not billed

				return [__("To Deliver and Bill"), "orange",
					"per_delivered,<,100|per_billed,<,100|status,!=,Closed"];
			} else {
				// not billed

				return [__("To Deliver"), "orange",
					"per_delivered,<,100|per_billed,=,100|status,!=,Closed"];
			}

		} else if ((doc.order_type === "Maintenance" || flt(doc.per_delivered, 6) == 100)
			&& flt(doc.per_billed, 6) < 100 && doc.status!=="Closed") {

			// to bill
			return [__("To Bill"), "orange", "per_delivered,=,100|per_billed,<,100|status,!=,Closed"];

		} else if((doc.order_type === "Maintenance" || flt(doc.per_delivered, 6) == 100)
			&& flt(doc.per_billed, 6) == 100 && doc.status!=="Closed") {

			return [__("Completed"), "green", "per_delivered,=,100|per_billed,=,100|status,!=,Closed"];
		}
	},
	onload: function(listview) {
		var method = "erpnext.selling.doctype.sales_order.sales_order.close_or_unclose_sales_orders";

		listview.page.add_menu_item(__("Close"), function() {
			listview.call_for_selected_items(method, {"status": "Closed"});
		});

		listview.page.add_menu_item(__("Re-open"), function() {
			listview.call_for_selected_items(method, {"status": "Submitted"});
		});

		// @custom
		// I didn't use `cur_list.add_button` to prevent using the field in query filters
		// This code in the callback simulates `cur_list.add_button`
		frappe.call({
			method: 'frappe.direction.customizations_2.get_percentage_completed_of_sales_order',
			callback: function(r) {
				if (!r || !r.message) return;

				var fieldtype = 'Data';
				var fieldname = 'percentage_completed';
				var label = frappe._('Completed');

				var $form_group = $('<div>');
				var $page_form = cur_list.$page.find('.page-form');
				var $form_control = $('<input>');

				$form_group.addClass('form-group frappe-control input-max-width col-md-2');
				$form_group.attr('data-fieldtype', fieldtype);
				$form_group.attr('data-fieldname', fieldname);
				$form_group.attr('title', label);
				$form_group.appendTo($page_form);
				$form_group.tooltip();

				$form_control.attr('type', 'text');
				$form_control.attr('autocomplete', 'off');
				$form_control.addClass('input-with-feedback form-control input-sm');
				$form_control.attr('maxlength', '140');
				$form_control.attr('data-fieldtype', fieldtype);
				$form_control.attr('data-fieldname', fieldname);
				$form_control.attr('placeholder', label);
				$form_control.attr('disabled', true);
				$form_control.val(label + ': ' + r.message + '%');
				$form_control.appendTo($form_group);
			}
		});
	}
};
