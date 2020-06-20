# -*- coding: utf-8 -*-
{
    'name': u"Reportes Path",
    'description': """
        Función: Este módulo agrega un campo para path dentro de la configuración(Ventas).
        Desarrollador: Rodrigo Dueñas,
        Funcional: Angel Linares 
    """,
    'author': 'ITSOLUTIONS-TOSCANA',
    'category': 'base',
    'version': '0.1',
    'depends': ['base','sale_management'],
    'data': [
        'views/res_config_settings_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}