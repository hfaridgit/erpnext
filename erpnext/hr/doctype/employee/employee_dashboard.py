from frappe import _

def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on the attendance of this Employee'),
		'fieldname': 'employee',
		'transactions': [
			{
				'label': _('Leave and Attendance'),
				'items': ['Attendance', 'Leave Application', 'Leave Allocation', 'Permit Application']
			},
			{
				'label': _('Payroll'),
				'items': ['Salary Structure', 'Salary Slip', 'Timesheet']
			},
			{
				'label': _('Training Events/Results'),
				'items': ['Training Event', 'Training Result']
			},
			{
				'label': _('Expense'),
				'items': ['Expense Claim']
			},
			{
				'label': _('Other'),
				'items': ['Employee Punishment', 'Employee Custody', 'Employee Loan', 'Employee Loan Application']
			},
			{
				'label': _('Evaluation'),
				'items': ['Appraisal']
			}
		]
	}