# -*- encoding: utf-8 -*-
{
	'name': 'Orden de Compra Personalizada',
	'category': 'purchase',
	'author': 'ITGRUPO-HELEO',
	'depends': ['sale_management','l10n_pe_toponyms','purchase','partner_confirm','purchase_order_contact','bi_purchase_discount'],
	'version': '1.0',
	'description':"""
		Función: Personaliza el formato de Orden de Compra del Odoo.
		Requiere: Multimoneda, multialmacen.
		Desarrollador: Rodrigo Dueñas.
		Funcional: Angel Linares.
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'views/purchase_order_view.xml',
		],
	'installable': True
}
