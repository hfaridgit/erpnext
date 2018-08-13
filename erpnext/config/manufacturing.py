from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Production"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Production Order",
					"description": _("Orders released for production."),
				},
				{
					"type": "doctype",
					"name": "Materials Planning Tool",
					"description": _("Generate Material Requests (MRP) for Production Orders."),
				},
				{
					"type": "doctype",
					"name": "Production Planning Tool",
					"description": _("Generate Material Requests (MRP) and Production Orders."),
				},
				{
					"type": "doctype",
					"name": "Production Forecast Tool",
					"description": _("Generate Material Requests (MRP) and Production Orders from Sales Forecast."),
				},
				{
					"type": "doctype",
					"name": "Stock Entry",
				},
				{
					"type": "doctype",
					"name": "Timesheet",
					"description": _("Time Sheet for manufacturing."),
				},
				{
					"type": "doctype",
					"name": "Production Time Log Tool",
					"description": _("Time log for Operations."),
				},

			]
		},
		{
			"label": _("Bill of Materials"),
			"items": [
				{
					"type": "doctype",
					"name": "BOM",
					"description": _("Bill of Materials (BOM)"),
					"label": _("Bill of Materials")
				},
				{
					"type": "doctype",
					"name": "BOM",
					"icon": "fa fa-sitemap",
					"label": _("BOM Browser"),
					"description": _("Tree of Bill of Materials"),
					"link": "Tree/BOM",
				},
				{
					"type": "doctype",
					"name": "Item",
					"description": _("All Products or Services."),
				},
				{
					"type": "doctype",
					"name": "Workstation",
					"description": _("Where manufacturing operations are carried."),
				},
				{
					"type": "doctype",
					"name": "Operation",
					"description": _("Details of the operations carried out."),
				},

			]
		},
		{
			"label": _("Tools"),
			"icon": "fa fa-wrench",
			"items": [
				{
					"type": "doctype",
					"name": "BOM Update Tool",
					"description": _("Replace BOM and update latest price in all BOMs"),
				},
			]
		},
		{
			"label": _("Setup"),
			"items": [
				{
					"type": "doctype",
					"name": "Manufacturing Settings",
					"description": _("Global settings for all manufacturing processes."),
				}, 
				{
					"type": "doctype",
					"name": "Costing Settings",
					"description": _("Global settings for Costing Calculations."),
				}
			]
		},
		{
			"label": _("Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Open Production Orders",
					"doctype": "Production Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Production Orders in Progress",
					"doctype": "Production Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Issued Items Against Production Order",
					"doctype": "Production Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Completed Production Orders",
					"doctype": "Production Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Production Order Quantity Variance",
					"doctype": "Production Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Production Order Output Quantity Variance",
					"doctype": "Production Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Production Variance Report",
					"doctype": "Production Order"
				},
				{ 
					"type": "page",
					"name": "production-analytics",
					"label": _("Production Analytics"),  
					"icon": "fa fa-bar-chart",
				},
				{ 
					"type": "report",
					"is_query_report": True,
					"name": "Operation Cost Distribution",
					"label": _("Operation Cost Distribution"),  
					"doctype": "Timesheet"
				},
				{ 
					"type": "report",
					"is_query_report": True,
					"name": "Operation Cost Distribution By Cost Center",
					"label": _("Operation Cost Distribution By Cost Center"),  
					"doctype": "Timesheet"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "BOM Search",
					"doctype": "BOM"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "BOM Stock Report",
					"doctype": "BOM"
				}
			]
		},
		{
			"label": _("Stock Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Items To Be Received",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"name": "Item Shortage Report",
					"route": "Report/Bin/Item Shortage Report",
					"doctype": "Purchase Receipt"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Batch-Wise Balance History",
					"doctype": "Batch"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Batch Item Expiry Status",
					"doctype": "Stock Ledger Entry"
				},
				# @custom
				{
					"type": "report",
					"is_query_report": True,
					"name": "Batch-Wise Balance",
					"doctype": "Stock Ledger Entry"
				},
				# @custom
				{
					"type": "report",
					"is_query_report": True,
					"name": "Batch-Wise Balance History Full",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Item Balance (Simple)",
					"doctype": "Bin"
				},
				# @custom
				{
					"type": "report",
					"is_query_report": True,
					"name": "Quantities in Specific Warehouses",
					"doctype": "Bin"
				}
			]
		},
		{
			"label": _("Help"),
			"icon": "fa fa-facetime-video",
			"items": [
				{
					"type": "help",
					"label": _("Bill of Materials"),
					"youtube_id": "hDV0c1OeWLo"
				},
				{
					"type": "help",
					"label": _("Production Planning Tool"),
					"youtube_id": "CzatSl4zJ2Y"
				},
				{
					"type": "help",
					"label": _("Production Order"),
					"youtube_id": "ZotgLyp2YFY"
				},
			]
		}
	]
