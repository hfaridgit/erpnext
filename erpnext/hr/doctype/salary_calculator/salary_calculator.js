// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

						// frappe.call({
						//	method: 'validate',
						//	args: {},
						//	callback: function(r) {frm.refresh_fields();},
						//	doc: frm.doc,
						//	freeze: true,
						//	freeze_message: 'Calculating Salary Please Wait ...'
						// });

frappe.ui.form.on("Salary Calculator", {
	setup: function(frm) {
		frm.set_query("salary_component", "earnings", function() {
			return {
				filters: {
					type: "earning"
				}
			}
		})
		frm.set_query("salary_component", "deductions", function() {
			return {
				filters: {
					type: "deduction"
				}
			}
		})
	},

	refresh: function(frm) {
	    frm.disable_save();
		frm.add_custom_button(__('Calculate'), function() {
						//var callback = function (r) { cur_frm.refresh_fields();	};
						//$c('runserverobj', { 'method': 'validate', 'docs': cur_frm.doc }, callback); 
						 frappe.call({
							method: 'validate',
							args: {},
							callback: function(r) {frm.refresh_fields();},
							doc: frm.doc,
							freeze: true,
							freeze_message: 'Calculating Salary Please Wait ...'
						 });
					});
		var salary_detail_fields = ['formula', 'abbr', 'statistical_component']
		cur_frm.fields_dict['earnings'].grid.set_column_disp(salary_detail_fields,false);
		cur_frm.fields_dict['deductions'].grid.set_column_disp(salary_detail_fields,false);
	},	

})

frappe.ui.form.on('Salary Detail', {
	earnings_remove: function(frm, dt, dn) {
		calculate_all(frm.doc, dt, dn);
	},
	deductions_remove: function(frm, dt, dn) {
		calculate_all(frm.doc, dt, dn);
	}
})

var calculate_all = function(doc, dt, dn) {
	calculate_earning_total(doc, dt, dn);
	calculate_ded_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
}

cur_frm.cscript.amount = function(doc,dt,dn){
	var child = locals[dt][dn];
	if(!doc.salary_structure){
		frappe.model.set_value(dt,dn, "default_amount", child.amount)
	}
	calculate_all(doc, dt, dn);
}

cur_frm.cscript.depends_on_lwp = function(doc,dt,dn){
	calculate_earning_total(doc, dt, dn, true);
	calculate_ded_total(doc, dt, dn, true);
	calculate_net_pay(doc, dt, dn);
	refresh_many(['amount','gross_pay', 'rounded_total', 'net_pay']);
};

// Calculate earning total
// ------------------------------------------------------------------------
var calculate_earning_total = function(doc, dt, dn, reset_amount) {

	var tbl = doc.earnings || [];
	var total_earn = 0;
	for(var i = 0; i < tbl.length; i++){
		if(cint(tbl[i].depends_on_lwp) == 1) {
			tbl[i].amount =  Math.round(tbl[i].default_amount);
		} else if(reset_amount) {
			tbl[i].amount = tbl[i].default_amount;
		}
		if(!tbl[i].do_not_include_in_total) {
			total_earn += flt(tbl[i].amount);

		}
	}
	doc.gross_pay = total_earn;
	refresh_many(['earnings', 'amount','gross_pay']);

}

// Calculate deduction total
// ------------------------------------------------------------------------
var calculate_ded_total = function(doc, dt, dn, reset_amount) {
	var tbl = doc.deductions || [];
	var total_ded = 0;
	for(var i = 0; i < tbl.length; i++){
		if(cint(tbl[i].depends_on_lwp) == 1) {
			tbl[i].amount = Math.round(tbl[i].default_amount);
		} else if(reset_amount) {
			tbl[i].amount = tbl[i].default_amount;
		}
		if(!tbl[i].do_not_include_in_total) {
			total_ded += flt(tbl[i].amount);
		}
	}
	doc.total_deduction = total_ded;
	refresh_many(['deductions', 'total_deduction']);
}

// Calculate net payable amount
// ------------------------------------------------------------------------
var calculate_net_pay = function(doc, dt, dn) {
	doc.net_pay = flt(doc.gross_pay) - flt(doc.total_deduction);
	doc.rounded_total = Math.round(doc.net_pay);
	refresh_many(['net_pay', 'rounded_total']);
}

// validate
// ------------------------------------------------------------------------
cur_frm.cscript.validate = function(doc, dt, dn) {
	calculate_all(doc, dt, dn);
}

