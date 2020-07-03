# -*- encoding: utf-8 -*-
{
	'name': 'Analisis de Vencimientos - TOSCANA',
	'category': 'account',
	'author': 'ITGRUPO-TOSCANA',
	'depends': ['account_balance_doc_rep_it'],
	'version': '1.0',
	'description':"""
	Sub-menu para reportes con Analisis de Vencimientos.
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/ir.model.access.csv',
		'wizards/maturity_analysis_rep.xml',
		'views/maturity_analysis_book.xml'
		],
	'installable': True
}
