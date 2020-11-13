# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Delivery Note, Sale and Stock Integration",

    'summary': """
       Integration between Ddt and sale_stock module""",

    'description': """
        Integration between Ddt and sale_stock module
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.0.7',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'l10n_it_ddt_extension_isa',
        'sale_stock',
        'sale',
        'stock',
        'l10n_it_ddt_sale_integration',
        'l10n_it_ddt_stock_integration',
        'l10n_it_shipping_info_sale_stock_integration',
        'delivery',
        'product',
    ],

    # always loaded
    'data': [
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/stock_move.xml',
        'views/l10n_it_ddt.xml',
    ],
    'auto_install': True,
}
