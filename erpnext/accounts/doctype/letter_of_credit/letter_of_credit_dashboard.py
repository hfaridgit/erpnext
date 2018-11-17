from frappe import _

def get_data():
	return {
		'fieldname': 'project',
		'transactions': [
			{
				'label': _('Stock'),
				'items': ['Purchase Receipt', 'Landed Cost Voucher']
			},
			{
				'label': _('Accounting'),
				'items': ['Purchase Invoice', 'Journal Entry', 'Payment Entry']
			},
		]
	}