// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Change Leave Approver Tool', {
	refresh: function(frm) {
		frm.disable_save();
		if (frm.hhh==1) {
			frm.set_value("company", undefined);
			frm.hhh = 0;
		}
		erpnext.change_leave_approver_tool.load_employees(frm);
	},
	
	onload: function(frm) {
		frm.doc.department = frm.doc.branch = frm.doc.company = frm.doc.business_unit = "All";
		frm.hhh = 1;
		erpnext.change_leave_approver_tool.load_employees(frm);
	},

	approver: function(frm) {
		erpnext.change_leave_approver_tool.load_employees(frm);
	},

	department: function(frm) {
		erpnext.change_leave_approver_tool.load_employees(frm);
	},

	branch: function(frm) {
		erpnext.change_leave_approver_tool.load_employees(frm);
	},

	company: function(frm) {
		erpnext.change_leave_approver_tool.load_employees(frm);
	}, 
	business_unit: function(frm) {
		erpnext.change_leave_approver_tool.load_employees(frm);
	}
	
});


erpnext.change_leave_approver_tool = {
	load_employees: function(frm) {
		if(frm.doc.approver) {
			frappe.call({
				method: "erpnext.hr.doctype.change_leave_approver_tool.change_leave_approver_tool.get_employees",
				args: {
					approver: frm.doc.approver,
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
			<button class="btn btn-primary btn-mark-present btn-xs"></button>\
			<button class="btn btn-default btn-mark-absent btn-xs"></button></div>')

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
			.html(__('Add Approver'))
			.on("click", function() {
				if(!frm.doc.approver) {
					frappe.msgprint(__("Please Choose Approver."));
					return
				}
				var employee_approver = [];
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						employee_approver.push(employee[i]);
					}
				});
				
				frappe.call({
					method: "erpnext.hr.doctype.change_leave_approver_tool.change_leave_approver_tool.mark_employee_approver",
					args:{
						"employee_list":employee_approver,
						"approver":frm.doc.approver
					},

					callback: function(r) {
						erpnext.change_leave_approver_tool.load_employees(frm);

					}
				});
			});

		mark_employee_toolbar.find(".btn-mark-absent")
			.html(__('Remove Approver'))
			.on("click", function() {
				frappe.call({
					method: "erpnext.hr.doctype.change_leave_approver_tool.change_leave_approver_tool.unmark_employee_approver",
					args:{
						approver: frm.doc.approver,
						department: frm.doc.department,
						branch: frm.doc.branch,
						company: frm.doc.company, 
						business_unit: frm.doc.business_unit
					},

					callback: function(r) {
						erpnext.change_leave_approver_tool.load_employees(frm);

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

