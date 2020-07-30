{
	"name": "Letras Toscana",
	"version": "1.0",
	"depends": [
		"vit_dotmatrix",
		"account_letras_it",
		"account_base_it",
		"print_letters",
		'base',
		'stock_remission_guide'
	],
	"author": "ITSOLUTIONS-TOSCANA",
	'website': 'https://itgrupo-solutions.com/',
	"description": """
		-Función: Esta solo es una plantilla que se imprimira las letras en la impresora matricial de la empresa Toscana, ya que se ajusta a sus medidas de impresion.
		-Desarrollador: Rodrigo Dueñas,
		-Funcional: Jorge Salinas. 
	""",
	"data": [
		"data/templates.xml",
		"views/res_currency_view.xml",
		"views/account_letras_payment_view.xml",
		"views/sale_order_view.xml",
		"reports/report_letters.xml",
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}