# -*- coding: utf-8 -*-
{
    'name': u"Seguimiento de Confirmación",
    'description': """
        -Función: Este módulo permite saber quien fue el partner que confirmo:
        1)Pedido de Venta
        2)Orden de Compra
        -Desarrollador: Rodrigo Dueñas,
        -Funcional: Angel Linares 
    """,
    'author': 'ITSOLUTIONS-TOSCANA',
    'category': 'base',
    'version': '0.1',
    'depends': ['base','sale_management','purchase'],
    'data': [
        'views/purchase_order_view.xml',
         'views/sale_order_view.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}