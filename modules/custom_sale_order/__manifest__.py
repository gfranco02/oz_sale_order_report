# -*- encoding: utf-8 -*-
{
	'name': 'Orden de Venta Personalizada',
	'category': 'sale',
	'author': 'ITGRUPO-TOSCANA',
	'depends': ['sale_base_it', 'l10n_pe_toponyms', 'report_it', 'partner_confirm','bo_report_base'],
	'version': '1.0',
	'description':"""
		Función: Personaliza el formato de Orden de Venta del Odoo.
		Requiere: Multimoneda, multialmacen, Descuentos.
		Desarrollador: Rodrigo Dueñas
		Funcional: Angel Linares
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'views/sale_order_view.xml',
		],
	'installable': True
}
