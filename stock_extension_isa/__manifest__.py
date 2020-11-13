# -*- coding: utf-8 -*-
{
    'name': "ISA Extension: Stock",

    'summary': """
        Provide some basic functionalities:
        - A default modules filter to get all modules developed by ISA S.r.L.
        - The translation for all the modules developed by ISA S.r.L.
    """,

    'description': """
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations',
    'version': '13.0.0.1.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'sale_stock',
        'sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_move_quantity_owner_info.xml',
        'views/stock_picking.xml',
        'views/product.xml'
    ]
}
