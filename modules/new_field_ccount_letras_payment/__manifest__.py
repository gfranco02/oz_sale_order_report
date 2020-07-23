# -*- encoding: utf-8 -*-
{
	'name': u'Codigo unico de Banco y Agencia de Envio',
	'category': 'reports',
	'author': 'ITGRUPO-TOSCANA',
	'depends': ['account_letras_it','stock_remission_guide'],
	'version': '1.0.0',
	'description':"""
	Agrega un (Codigo unico de Banco) en el tree dentro de canje de letras y una agencia de envio dentro del stock_picking.
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'views/account_letras_payment_view.xml',
		'views/sale_order_view.xml',
		],
	'installable': True
}
