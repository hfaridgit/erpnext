// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'business_unit', 'business_unit');
cur_frm.add_fetch('employee', 'designation', 'employee_job');
cur_frm.add_fetch('employee', 'department', 'employee_department');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name'); 

frappe.ui.form.on('Mission Planning', {
	refresh: function(frm) {
		if (frm.doc.__islocal) {
			frm.flg = 1;
			//var now = new Date();
			//var onejan = new Date(now.getFullYear(), 0, 1);
			//w = Math.ceil( (((now - onejan) / 86400000) + onejan.getDay()) / 7 )-1;
			w = moment().isoWeek();
			frm.set_value("year",(new Date()).getFullYear());
			frm.set_value("week",w);
		} else {
			frm.flg = 0;
			frm.toggle_enable("year",false);
			frm.toggle_enable("week",false);
		}
		cur_frm.$wrapper.find(".grid-add-row, .grid-add-multiple-rows").addClass('hide');
		//To hide checkboxes beside each line in grid:
		cur_frm.$wrapper.find(".grid-row-check").addClass('hide');
		//To hide Delete Row button for a grid:
		cur_frm.$wrapper.find(".grid-delete-row").addClass('hide');
		cur_frm.$wrapper.find(".btn-open-row").on('click', function() {	cur_frm.$wrapper.find(".grid-delete-row").addClass('hide'); return false; });

	},
	validate: function(frm) {
		var tot_office = 0;
		var tot_holiday = 0;
		var tot_mission = 0;
		$.each(frm.doc.mission_details || [], function(i, row) {
			if(row.office==1) {
				tot_office += 1;
			}
			if(row.holiday==1) {
				tot_holiday += 1;
			}
			if(row.mission_place_1 || row.mission_place_2 || row.mission_place_3 || row.mission_place_4 || row.mission_place_5 || row.mission_place_6 || row.mission_place_7 || row.mission_place_8 || row.mission_place_9 || row.mission_place_10) {
				tot_mission += 1;
			}
		});
		frm.set_value("mission_numbers", tot_mission) ; 
		frm.set_value("office_numbers", tot_office) ; 
		frm.set_value("holiday_numbers", tot_holiday) ; 
		//if (!frm.doc.__islocal && tot_mission+tot_office+tot_holiday!=7) {
		//	frappe.throw(__("Mission Days + Office Days + Holidays  should be = 7"));
		//}
	},
});

frappe.ui.form.on('Mission Detail Planning', {
	office: function(frm, dt, dn) {
		var d = locals[dt][dn]; 
		if(d.office==1) {
			frm.set_value("office_numbers", frm.doc.office_numbers+1); 
			frappe.model.set_value(dt, dn, "holiday", 0);
		} else {
			frm.set_value("office_numbers", frm.doc.office_numbers-1); 
		}
		frm.set_value("mission_numbers", 7-frm.doc.office_numbers-frm.doc.holiday_numbers); 
	},
	holiday: function(frm, dt, dn) {
		var d = locals[dt][dn];
		if(d.holiday==1) {
			frm.set_value("holiday_numbers", frm.doc.holiday_numbers+1); 
			frappe.model.set_value(dt, dn, "office", 0);
		} else {
			frm.set_value("holiday_numbers", frm.doc.holiday_numbers-1); 
		}
		frm.set_value("mission_numbers", 7-frm.doc.office_numbers-frm.doc.holiday_numbers); 
	},
});
