# -*- coding: utf-8 -*-
{
    'name': 'Grupos de Seguridad',
    'version': '1.0',
    'summary': 'Modulo que agrega grupos de seguridad a campos base del Odoo',
    'description':"""
		-Función: Agrega un grupo de seguridad a:
            1)Botónes Confirmar dentro de Cotización
            2)Menú Extracto Bancario.
            3)Confirmar pedidos de compra.
		-Desarrollador: Rodrigo Dueñas.
		-Funcional: Angel Linares.
	""",
    'author': 'ITGRUPO-TOSCANA',
    'depends': ['sale_management', 'purchase', 'account_base_it'],
    'data': [
        'security/groups.xml',
        'views/views.xml',
    ],
}
