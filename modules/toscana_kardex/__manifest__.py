{
	"name": "Kardex - Toscana",
	"version": "1.0",
	"depends": [
		"kardex",
	],
	"author": "ITSOLUTIONS-TOSCANA",
	'website': 'https://itgrupo-solutions.com/',
	"description": """
==============
Kardex Toscana
==============
- Extensión de kardex personalizado para Toscana
	""",
	"data": [
		#"data/templates.xml",
		##"views/res_currency_view.xml",
		#"views/account_letras_payment_view.xml",
		##"views/sale_order_view.xml",
		"views/stock_picking.xml",
		'wizard/assign_production_cost.xml',
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}