# -*- encoding: utf-8 -*-
{
	'name': 'Orden de Venta Personalizada',
	'category': 'sale',
	'author': 'ITGRUPO-HELEO',
	'depends': ['sale_management','l10n_pe_toponyms','report_path','export_file_manager_it','partner_confirm','sale_order_contact'],
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
