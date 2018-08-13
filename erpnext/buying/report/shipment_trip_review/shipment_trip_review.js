// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
			//$('<div id="myModal" style="display: none; position: fixed; z-index: 9999; padding-top: 100px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgb(0,0,0); background-color: rgba(0,0,0,0.4);">' +
			//	'<div style="background-color: #fefefe; margin: auto; padding: 20px; border: 1px solid #888; width: 50%; height: 400px;">' +
			//		'<span id="myClose" style="color: #aaaaaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>' +
			//		'<div style="background-color: #fefefe; margin: auto; padding: 20px; border: 1px solid #888; width: 100%; height: 90%;overflow-x: scroll; overflow-y: scroll;">' +
			//		'<div id="edittable"></div>' +
			//	'</div></div>' +
			//'</div>').appendTo($("body"));
			$('<div id="myModal" style="display: none; position: fixed; z-index: 9999; padding-top: 100px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgb(0,0,0); background-color: rgba(0,0,0,0.4);">' +
			'<div style="box-shadow: 8px 8px 10px #575757; width: 250px; margin: auto; text-align: center; background-color: #ffffff";>' +
					'<div id="edittable"></div>' +
				'</div>' +
			'</div>').appendTo($("body"));
			var modal = document.getElementById('myModal');

			// Get the button that opens the modal
			//var span = document.getElementById("myClose");
			//span.onclick = function() {
			//	modal.style.display = "none";
			//}
			window.onclick = function(event) {
				if (event.target == modal) {
					modal.style.display = "none";
				}
			}	

frappe.query_reports["Shipment Trip Review"] = {
	onload: function(report) {
		report.page.add_inner_button(__("Get Data From Invoices"), function() {
				frappe.call({
					method: "erpnext.buying.report.shipment_trip_review.shipment_trip_review.generate_data", 
					callback: (r) => {
						frappe.query_report.refresh();
					}
				});
		});
	},
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"business_unit",
			"label": __("Business Unit"),
			"fieldtype": "Link",
			"options": "Business Unit",
			"default": frappe.defaults.get_user_default("Business Unit"),
			"reqd": 1
		},
		{
			"fieldname":"exclude_completed",
			"label": __("Exclude Completed"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
		},
	],
	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
		//value = dataContext.account_name;
		var cell_color = "#FFFFFF"
		if (dataContext.status == 'Completed') {
			cell_color = "#A6FFA6";
			if (columnDef.df.fieldname != 'purchase_order' && columnDef.df.fieldname != 'purchase_invoice' && columnDef.df.fieldname != 'item_code') {
				columnDef.df.link_onclick = "#";
			}
			var $value = $(value).css({"display":"block","width":"100%","background-color": cell_color, "cursor": "default"});
		} else {
			if (columnDef.df.fieldname != 'purchase_order' && columnDef.df.fieldname != 'purchase_invoice' && columnDef.df.fieldname != 'item_code') {
				columnDef.df.link_onclick = "frappe.query_reports['Shipment Trip Review'].change_data('" + columnDef.df.label + "', '" + 
				columnDef.df.actualtype + "', '" + columnDef.df.actualoptions + "', '" + columnDef.df.fieldname + "', " + JSON.stringify(dataContext) + ")";
			}
		}
		if (columnDef.df.fieldname=="bank_acceptance_duration" && dataContext.bank_acceptance_duration>4) {
			cell_color = "#77FFFF";
		}
		if (columnDef.df.fieldname=="customs_release_duration" && dataContext.customs_release_duration>10) {
			cell_color = "#FFAB2D";
		}
		if (columnDef.df.fieldname=="total_duration" && dataContext.total_duration>14) {
			cell_color = "#FF9B9B";
		}
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (columnDef.df.fieldname=="qty" || columnDef.df.fieldname=="amount" || columnDef.df.fieldname=="currency") {
			var $value = $(value).css({"display":"block","width":"100%","background-color": cell_color, "cursor": "default"});
		} else {
			var $value = $(value).css({"display":"block","width":"100%","background-color": cell_color});
		}
		value = $value.wrap("<p></p>").parent().html();
		return value;
	},
	"change_data": function(fldlbl, fldtyp, opts, field, values) {
		if(values.docstatus>0) { frappe.msgprint(__("Transaction Already Submitted.")); return; }
		if( field=='qty' || field=='amount' || field=='currency') { return; }

		if (fldtyp=="Select") {
			opts = opts.split(",");
		}
		frappe.prompt({fieldname:field, options: opts, fieldtype:fldtyp,  
		label: fldlbl, reqd: 0}, function(data) {
				frappe.call({
					method: "frappe.client.set_value",
					args: {
						doctype: "Supplier Shipment Trip",
						name: values.name,
						fieldname: field,
						value: data[field],
					},
					callback: (r) => {
						frappe.query_reports['Shipment Trip Review'].add_log(field, values[field], values.name, data[field]);
					}
				});
		}, __("Change Value for Shipment  " + values.shipment_no));
	}, 
	"show_img": function(values) {
			document.getElementById("edittable").innerHTML = '<img src="' + frappe.urllib.get_base_url() + values.image + '"  style="width:100%">' +
						'<h2>'+values.employee_name+'</h2>' +
						'<p style="color: grey; font-size: 16px;">'+values.designation +'</p>' +
					'<p>' + values.employee+ '</p>' +
				'<p><button style="border: none;  outline: 0;  display: inline-block;  padding: 8px;  color: white;  background-color: #000;' + 
									'text-align: center;  cursor: pointer;  width: 100%;  font-size: 18px;" ' + 
									' onMouseOver="this.style.opacity=0.7"  onMouseOut="this.style.opacity=1"' + 
				'onclick="frappe.query_reports[\'Shipment Trip Review\'].open_form(' + values.employee + ')">View Details</button></p>';
			var modal = document.getElementById('myModal');
			modal.style.display = "block";
	}, 
	"open_form": function(doctype, docname) {
		if (!doctype || !docname) return;
		//modal.style.display = "none";

		frappe.set_route("Form", doctype, docname);
	},
	"add_log": function(field, old_value, key_name, new_value) {
		var clog0 = frappe.model.make_new_doc_and_get_name('Changes Log');
		clog = locals['Changes Log'][clog0];
		clog.report_name = frappe.query_report.report_name;
		clog.fieldname = field;
		if (old_value!="___") {
			clog.old_value = old_value;
		}
		clog.new_value = new_value;
		clog.record_key = "name";
		clog.key_name = key_name;
			frappe.call({
						method: "frappe.client.insert",
						args: {
							doc: clog
						},
						callback: function(r) {
							frappe.call({
								method: "frappe.client.submit",
								args: {
									doc: r.message
								},
								callback: function(r) {
									frappe.query_report.refresh();
								}
							});
						}
			});			
	}, 

}

