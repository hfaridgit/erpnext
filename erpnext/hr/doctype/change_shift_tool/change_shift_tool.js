// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Change Shift Tool', {
	refresh: function(frm) {
		frm.disable_save();
		if (frm.hhh==1) {
			frm.set_value("company", undefined);
			frm.hhh = 0;
		}
	},
	
	onload: function(frm) {
		frm.doc.department = frm.doc.branch = frm.doc.company = frm.doc.business_unit = "All";
		frm.set_value("date", frappe.datetime.get_today());
		frm.hhh = 1;
		erpnext.change_shift_tool.load_employees(frm);
	},

	date: function(frm) {
		erpnext.change_shift_tool.load_employees(frm);
	},

	shift: function(frm) {
		erpnext.change_shift_tool.load_employees(frm);
	},

	department: function(frm) {
		erpnext.change_shift_tool.load_employees(frm);
	},

	branch: function(frm) {
		erpnext.change_shift_tool.load_employees(frm);
	},

	company: function(frm) {
		erpnext.change_shift_tool.load_employees(frm);
	}, 
	business_unit: function(frm) {
		erpnext.change_shift_tool.load_employees(frm);
	}
	
});


erpnext.change_shift_tool = {
	load_employees: function(frm) {
		if(frm.doc.date) {
			frappe.call({
				method: "erpnext.hr.doctype.change_shift_tool.change_shift_tool.get_employees",
				args: {
					date: frm.doc.date,
					shift: frm.doc.shift,
					department: frm.doc.department,
					branch: frm.doc.branch,
					company: frm.doc.company, 
					business_unit: frm.doc.business_unit
				},
				callback: function(r) {
					if(r.message['unmarked'].length > 0) {
						unhide_field('unmarked_employees_section')
						if(!frm.employee_area) {
							frm.employee_area = $('<div>')
							.appendTo(frm.fields_dict.employees_html.wrapper);
						}
						frm.EmployeeSelector = new erpnext.EmployeeSelector(frm, frm.employee_area, r.message['unmarked'])
					}
					else{
						hide_field('unmarked_employees_section')
					}

					if(r.message['marked'].length > 0) {
						unhide_field('marked_employees_section')
						if(!frm.marked_employee_area) {
							frm.marked_employee_area = $('<div>')
								.appendTo(frm.fields_dict.marked_employees_html.wrapper);
						}
						frm.marked_employee = new erpnext.MarkedEmployee(frm, frm.marked_employee_area, r.message['marked'])
					}
					else{
						hide_field('marked_employees_section')
					}
				}
			});
		}
	}
}

erpnext.MarkedEmployee = Class.extend({
	init: function(frm, wrapper, employee) {
		this.wrapper = wrapper;
		this.frm = frm;
		this.make(frm, employee);
	},
	make: function(frm, employee) {
		var me = this;
		$(this.wrapper).empty();

		var row;
		$.each(employee, function(i, m) {
			var employees_icon = "fa fa-check";
			var color_class = "";

			if (i===0 || i % 4===0) {
				row = $('<div class="row"></div>').appendTo(me.wrapper);
			}

			$(repl('<div class="col-sm-3 %(color_class)s">\
				<label class="marked-employee-label"><span class="%(icon)s"></span>\
				%(employee)s</label>\
				</div>', {
					employee: m.employee_name,
					icon: employees_icon,
					color_class: color_class
				})).appendTo(row);
		});
	}
});


erpnext.EmployeeSelector = Class.extend({
	init: function(frm, wrapper, employee) {
		this.wrapper = wrapper;
		this.frm = frm;
		this.make(frm, employee);
	},
	make: function(frm, employee) {
		var me = this;

		$(this.wrapper).empty();
		var employee_toolbar = $('<div class="col-sm-12 top-toolbar">\
			<button class="btn btn-default btn-add btn-xs"></button>\
			<button class="btn btn-xs btn-default btn-remove"></button>\
			</div>').appendTo($(this.wrapper));

		var mark_employee_toolbar = $('<div class="col-sm-12 bottom-toolbar">\
			<button class="btn btn-primary btn-mark-present btn-xs"></button></div>')

		employee_toolbar.find(".btn-add")
			.html(__('Check all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if(!$(check).is(":checked")) {
						check.checked = true;
					}
				});
			});

		employee_toolbar.find(".btn-remove")
			.html(__('Uncheck all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						check.checked = false;
					}
				});
			});

		mark_employee_toolbar.find(".btn-mark-present")
			.html(__('Change Shift'))
			.on("click", function() {
				if(!frm.doc.shift) {
					frappe.msgprint(__("Please Choose Shift."));
					return
				}
				var employee_shift = [];
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						employee_shift.push(employee[i]);
					}
				});
				
				frappe.call({
					method: "erpnext.hr.doctype.change_shift_tool.change_shift_tool.mark_employee_shift",
					args:{
						"employee_list":employee_shift,
						"shift":frm.doc.shift,
						"date":frm.doc.date,
						"company":frm.doc.company, 
						"business_unit":frm.doc.business_unit
					},

					callback: function(r) {
						erpnext.change_shift_tool.load_employees(frm);

					}
				});
			});


		var row;
		$.each(employee, function(i, m) {
			if (i===0 || (i % 4) === 0) {
				row = $('<div class="row"></div>').appendTo(me.wrapper);
			}

			$(repl('<div class="col-sm-3 unmarked-employee-checkbox">\
				<div class="checkbox">\
				<label><input type="checkbox" class="employee-check" employee="%(employee)s"/>\
				%(employee)s</label>\
				</div></div>', {employee: m.employee_name})).appendTo(row);
		});

		mark_employee_toolbar.appendTo($(this.wrapper));
	}
});

