# -*- encoding: utf-8 -*-
{
	'name': u'Codigo unico de Banco',
	'category': 'reports',
	'author': 'ITGRUPO-TOSCANA',
	'depends': ['account_letras_it'],
	'version': '1.0.0',
	'description':"""
	Agrega un (Codigo unico de Banco) en el tree dentro de canje de letras.
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'views/account_letras_payment_view.xml',
		],
	'installable': True
}
