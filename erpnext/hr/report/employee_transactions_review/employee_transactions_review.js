// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
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

frappe.query_reports["Employee Transactions Review"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			on_change: function(report) {
						frappe.call({
							method: "erpnext.hr.report.employee_transactions_review.employee_transactions_review.get_employees",
							args: {
								company: frappe.query_report_filters_by_name.company.get_value(),
								branch: frappe.query_report_filters_by_name.branch.get_value()
							},
							callback: (r) => {
								window.em = r.message;
								window.emp = 0;
								frappe.query_report_filters_by_name.employee.set_value(window.em[0][0]);
							}
						});
			},
			"reqd": 1
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Int",
			"default": frappe.datetime.str_to_obj(frappe.datetime.get_today()).getFullYear(),
			"width": "50px",
			"reqd": 1
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Int",
			"default": frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()+1,
			"width": "50px",
			"reqd": 1
		},
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"default": frappe.defaults.get_user_default("Branch"),
			on_change: function(report) {
						frappe.call({
							method: "erpnext.hr.report.employee_transactions_review.employee_transactions_review.get_employees",
							args: {
								company: frappe.query_report_filters_by_name.company.get_value(),
								branch: frappe.query_report_filters_by_name.branch.get_value()
							},
							callback: (r) => {
								window.em = r.message;
								window.emp = 0;
								frappe.query_report_filters_by_name.employee.set_value(window.em[0][0]);
							}
						});
			},
			"reqd": 1
		},
		{
			"fieldname":"previous",
			"label": __("Prev"),
			"fieldtype": "Button",
		},
		{
			"fieldname":"next",
			"label": __("Next"),
			"fieldtype": "Button",
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"reqd": 0
		}, 
	],
	"onload": function(report) {
		window.emp = 0;			
		window.em = [];
		frappe.query_report_filters_by_name.previous.$input.click(function(report) {
			window.emp = window.emp-1;
			if (window.emp<0) { 
				window.emp=0; 
			} else {
				frappe.query_report_filters_by_name.employee.set_value(window.em[window.emp][0]);
			}
		});
		frappe.query_report_filters_by_name.next.$input.click(function(report) {
			window.emp = window.emp+1;
			if (window.emp>window.em.length-1) {
				window.emp = window.em.length-1;
			} else {
				frappe.query_report_filters_by_name.employee.set_value(window.em[window.emp][0]);
			}
		});
	},
	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
		//value = dataContext.account_name;
		var cell_color = "#FFFFFF"
		switch (columnDef.df.fieldname) {
			case "employee":
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].show_img(" + JSON.stringify(dataContext) + ")";
				break;
			case "mission_application":
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].new_mission(" + JSON.stringify(dataContext) + ")";
				break;
			case "leave_application": 
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].new_leave(" + JSON.stringify(dataContext) + ")";
				break;
			case "is_leave": 
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].new_leave(" + JSON.stringify(dataContext) + ")";
				break;
			case "half_day": 
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].new_leave(" + JSON.stringify(dataContext) + ")";
				break;
			case "shift": 
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].change_shift(" + JSON.stringify(dataContext) + ")";
				break;
			case "permit_application":
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].new_permit(" + JSON.stringify(dataContext) + ")";
				break;
			case "punishment":
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].open_punishment(" + JSON.stringify(dataContext) + ")";
				break;
			case "time_in": 
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].change_time('" + columnDef.df.label + "', '" + 
				columnDef.df.actualtype + "', '" + columnDef.df.actualoptions + "', '" + columnDef.df.fieldname + "', " + JSON.stringify(dataContext) + ")";
				break;
			case "time_out": 
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].change_time('" + columnDef.df.label + "', '" + 
				columnDef.df.actualtype + "', '" + columnDef.df.actualoptions + "', '" + columnDef.df.fieldname + "', " + JSON.stringify(dataContext) + ")";
				break;
			default: 
				columnDef.df.link_onclick = "frappe.query_reports['Employee Transactions Review'].change_data('" + columnDef.df.label + "', '" + 
				columnDef.df.actualtype + "', '" + columnDef.df.actualoptions + "', '" + columnDef.df.fieldname + "', " + JSON.stringify(dataContext) + ")";
		}
		if (dataContext.time_in !='___') {
		    var time1 = dataContext.time_in.split(/:/);
			var t_in = time1[0] * 3600 + time1[1] * 60 + time1[2];
			if (dataContext.shift_late_time) {
				var time2 = dataContext.shift_late_time.split(/:/);
				var lt_t = time2[0] * 3600 + time2[1] * 60 + time2[2];
			} else { lt_t = t_in-1000 }
		}

		if (columnDef.df.fieldname=="lateness_minutes2") {
			var a = dataContext.lateness_minutes;
			var hours = Math.trunc(a/60);
			var minutes = a % 60;
			dataContext.lateness_minutes2 = hours +":"+ minutes;
			value = hours +":"+ minutes;
		}
		if (columnDef.df.fieldname=="early_exit_minutes2") {
			var a = dataContext.early_exit_minutes;
			var hours = Math.trunc(a/60);
			var minutes = a % 60;
			dataContext.early_exit_minutes2 = hours +":"+ minutes;
			value = hours +":"+ minutes;
		}
		if (columnDef.df.fieldname=="overtime_minutes2") {
			var a = dataContext.overtime_minutes; 
			var hours = Math.trunc(a/60);
			var minutes = a % 60;
			dataContext.overtime_minutes2 = hours +":"+ minutes;
			value = hours +":"+ minutes;
		}
		if (value=="0:0") {
			value = "";
		}
		if (columnDef.df.fieldname=="time_in" && lt_t<t_in) {
			cell_color = "#FF9B9B";
		}
		if (dataContext.is_holiday =='___' && dataContext.is_leave =='___' && columnDef.df.fieldname=="time_in" && dataContext.time_in =='___') {
			cell_color = "#FF9B9B";
		}
		if (dataContext.is_holiday =='___' && dataContext.is_leave =='___' && columnDef.df.fieldname=="time_out" && dataContext.time_out =='___') {
			cell_color = "#FF9B9B";
		}
		if (columnDef.df.fieldname=="bus_delay" && dataContext.bus_delay !='___') {
			cell_color = "#77FFFF";
		}
		if (columnDef.df.fieldname=="lateness_minutes2" && dataContext.lateness_minutes > 5) {
			cell_color = "#FFAB2D";
		}
		if (columnDef.df.fieldname=="early_exit_minutes2" && dataContext.early_exit_minutes > 0) {
			cell_color = "#FFAB2D";
		}

		// *********  Holiday *******************
		if (dataContext.is_holiday !='___') {
			cell_color = "#FFFFC6";
		}
		
		// *********  Leave *******************
		if (dataContext.is_leave !='___') {
			cell_color = "#A6FFA6";
		}
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (columnDef.df.fieldname=="posting_date" || columnDef.df.fieldname=="day_name" || columnDef.df.fieldname=="attendance_hours" || columnDef.df.fieldname=="bus_time_in" 
			|| columnDef.df.fieldname=="lateness_minutes2" || columnDef.df.fieldname=="early_exit_minutes2" || columnDef.df.fieldname=="overtime_minutes2") {
			var $value = $(value).css({"display":"block","width":"100%","background-color": cell_color, "cursor": "default"});
		} else {
			var $value = $(value).css({"display":"block","width":"100%","background-color": cell_color});
		}
		$value = $value.prop('title', dataContext.posting_date + " - " + dataContext.day_name);
		value = $value.wrap("<p></p>").parent().html();
		return value;
	},
	"change_data": function(fldlbl, fldtyp, opts, field, values) {
		if(values.docstatus>0) { frappe.msgprint(__("Transaction Already Submitted.")); return; }
		if( field=="day_name" || field=="posting_date" || field=='bus_time_in' || field=='attendance_hours') { return; }
		if( field=="lateness_minutes2" || field=="early_exit_minutes2" || field=='bus_time_in' || field=='overtime_minutes2') { return; }
		if (fldtyp=="Select") {
			opts = opts.split(",");
		}
		frappe.prompt({fieldname:field, options: opts, fieldtype:fldtyp,  
		label: fldlbl, reqd: 0}, function(data) {
				frappe.call({
					method: "frappe.client.set_value",
					args: {
						doctype: "Employee Transactions",
						name: values.name,
						fieldname: field,
						value: data[field],
					},
					callback: (r) => {
						frappe.query_reports['Employee Transactions Review'].add_log(field, values[field], values.name, data[field]);
					}
				});
		}, __("Change Value for Employee  " + values.employee));
	}, 
	"change_time": function(fldlbl, fldtyp, opts, field, values) {
		if(values.docstatus>0) { frappe.msgprint(__("Transaction Already Submitted.")); return; }
		frappe.prompt({fieldname:field, options: opts, fieldtype:fldtyp,  
		label: fldlbl, reqd: 0}, function(data) {
				frappe.call({
					method: "erpnext.hr.doctype.employee_transactions_tool.employee_transactions_tool.change_time",
					args: {
						employee: values.employee,
						shift: values.shift,
						posting_date: values.posting_date, 
						fieldname: field, 
						key_name: values.name, 
						new_value: data[field]
					},
					callback: (r) => {
						frappe.query_reports['Employee Transactions Review'].add_log(field, values[field], values.name, data[field]);
					}
				});
		}, __("Change Value for Employee  " + values.employee));
	}, 
	"show_img": function(values) {
			document.getElementById("edittable").innerHTML = '<img src="' + frappe.urllib.get_base_url() + values.image + '"  style="width:100%">' +
						'<h2>'+values.employee_name+'</h2>' +
						'<p style="color: grey; font-size: 16px;">'+values.designation +'</p>' +
					'<p>' + values.employee+ '</p>' +
				'<p><button style="border: none;  outline: 0;  display: inline-block;  padding: 8px;  color: white;  background-color: #000;' + 
									'text-align: center;  cursor: pointer;  width: 100%;  font-size: 18px;" ' + 
									' onMouseOver="this.style.opacity=0.7"  onMouseOut="this.style.opacity=1"' + 
				'onclick="frappe.query_reports[\'Employee Transactions Review\'].open_form(' + values.employee + ')">View Details</button></p>';
			var modal = document.getElementById('myModal');
			modal.style.display = "block";
	}, 
	"open_form": function(emp) {
		if (!emp) return;
		modal.style.display = "none";

		frappe.set_route("Form", "Employee", emp);
	},
	"new_mission":  function(values) {
		if (values.mission_application !='___') {
			frappe.set_route("Form", "Leave Application", values.mission_application);
		} else {
			if(values.docstatus>0) { frappe.msgprint(__("Transaction Already Submitted.")); return; }
			frappe.prompt([{fieldname: "to_date", fieldtype: "Date",  label: "To Date", "default": values.posting_date, reqd: 1}, 
				{fieldname:"half_day", fieldtype:"Check",  label: "Half Day", "default": 0,  reqd: 0}], 
				function(data) { 
						frappe.call({
							method: "erpnext.hr.doctype.employee_transactions_tool.employee_transactions_tool.change_leave",
							args: {
								naming_series: "Mission/",
								leave_type: "مأمورية", 
								company: values.company,
								business_unit: values.business_unit,
								employee: values.employee,
								from_date: values.posting_date,
								to_date: data.to_date,
								half_day: data.half_day
							},
							callback: (r) => {
								frappe.query_report.refresh();
							}
						});
				}, __("Add Mission for Employee  " + values.employee));
		}
	}, 
	"new_leave":  function(vals) {
		if (vals.leave_application !='___') {
			frappe.set_route("Form", "Leave Application", vals.leave_application);
		} else {
			if(vals.docstatus>0) { frappe.msgprint(__("Transaction Already Submitted.")); return; }
			frappe.prompt([{fieldname: "leave_type", fieldtype: "Link", options: "Leave Type",  label: "Leave Type", reqd: 1, 
							"get_query": function() {
								return {
									query : "erpnext.hr.doctype.employee_transactions_tool.employee_transactions_tool.leave_query",
									filters: {'employee': vals.employee, 'posting_date': vals.posting_date}
								};
							}
				},
				{fieldname: "to_date", fieldtype: "Date",  label: "To Date", "default": vals.posting_date, reqd: 1}, 
				{fieldname:"half_day", fieldtype:"Check",  label: "Half Day", "default": 0,  reqd: 0}], 
				function(data) { 
						frappe.call({
							method: "erpnext.hr.doctype.employee_transactions_tool.employee_transactions_tool.change_leave",
							args: {
								naming_series: 'LAP/', 
								leave_type: data.leave_type, 
								company: vals.company,
								business_unit: vals.business_unit,
								employee: vals.employee,
								from_date: vals.posting_date,
								to_date: data.to_date,
								half_day: data.half_day
							},
							callback: (r) => {
								frappe.query_report.refresh();
							}
						});
				}, __("Add Leave for Employee  " + vals.employee));
		}
	}, 
	"new_permit":  function(values) {
		if (values.permit_application !='___') {
			frappe.set_route("Form", "Permit Application", values.permit_application);
		} else {
			if(values.docstatus>0) { frappe.msgprint(__("Transaction Already Submitted.")); return; }
			frappe.prompt([{fieldname: "total_units", fieldtype: "Int",  label: "Total Hours", "default": 1, reqd: 1},
							{fieldname: ", is_early_leave", fieldtype: "Check",  label: "Early Leave", "default": 0}], 
				function(data) { 
						frappe.call({
							method: "erpnext.hr.doctype.employee_transactions_tool.employee_transactions_tool.change_permit",
							args: {
								company: values.company,
								business_unit: values.business_unit,
								employee: values.employee,
								total_units: data.total_units,
								permit_date: values.posting_date,
								is_early_leave: data.is_early_leave
							},
							callback: (r) => {
								frappe.query_report.refresh();
							}
						});
				}, __("Add Permit for Employee  " + values.employee));
		}
	}, 
	"change_shift":  function(values) {
		if(values.docstatus>0) { frappe.msgprint(__("Transaction Already Submitted.")); return; }
		frappe.prompt({fieldname: "shift", fieldtype: "Link", options: "Shifts",  label: "Shift", reqd: 1}, 
			function(data) { 
					frappe.call({
						method: "erpnext.hr.doctype.employee_transactions_tool.employee_transactions_tool.change_shift",
						args: {
							company: values.company,
							business_unit: values.business_unit,
							employee: values.employee,
							shift: data.shift,
							posting_date: values.posting_date
						},
						callback: (r) => {
							frappe.query_report.refresh();
						}
					});
			}, __("Change Shift for Employee  " + values.employee));
	}, 
	"open_punishment": function(values) {
		if (values.punishment) {
			frappe.set_route("Form", "Employee Punishment", values.punishment);
		} 
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

