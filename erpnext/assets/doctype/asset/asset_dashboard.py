def get_data():
	return {
		'fieldname': 'asset_name', 
		'non_standard_fieldnames': {
			'Sales Invoice': 'asset',
			'Journal Entry': 'reference_name',
			'Purchase Invoice': 'asset'
		},
		'transactions': [
			{
				'label': ['Maintenance & Repair'],
				'items': ['Asset Maintenance', 'Asset Maintenance Log', 'Asset Repair']
			},
			{
				'label': ['Other'],
				'items': ['Sales Invoice', 'Purchase Invoice', 'Journal Entry']
			}
		]
	}