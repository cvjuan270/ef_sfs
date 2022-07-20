# -*- coding: utf-8 -*-
{
    'name': "Facturacion electronica con SFS_1.5",

    'summary': """
    Genera documentos electronicos a travez de la API del SFS_1.5 SUNAT""",

    'description': """
        Emite Facturas electronica Peru a travez del API SFS_1.5 SUNAT
    """,

    'author': "Juan Collado",
    'website': "cvjuan@gmail.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        'views/account_move_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
