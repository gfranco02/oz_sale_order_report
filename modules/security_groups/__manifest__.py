# -*- coding: utf-8 -*-
{
    'name': 'Grupos de Seguridad',
    'version': '1.0',
    'summary': 'Modulo que agrega grupos de seguridad a campos base del Odoo',
    'description':"""
		-Función: Agrega un grupo de seguridad a:
                    1)Botón Confirmar dentro de Cotización
		-Desarrollador: Rodrigo Dueñas.
		-Funcional: Angel Linares.
	""",
    'author': 'ITGRUPO-TOSCANA',
    'depends': ['sale_management', 'purchase'],
    'data': [
        'security/groups.xml',
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/product.xml',
    ],
    # 'images': [
    #     'static/description/icon.png',
    # ],
}
