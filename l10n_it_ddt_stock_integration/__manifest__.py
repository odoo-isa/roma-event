# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Delivery Note and Stock Integration",

    'summary': """
        Integration between Ddt and stock module""",

    'description': """
        Integration between Ddt and stock module
    """,

    'author': "ISA S.r.L.",
    'website': "https://isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.0.6',

    # any module necessary for this one to work correctly
    'depends': [
        'l10n_it_ddt_extension_isa',
        'l10n_it_shipping_info_stock_integration',
        'stock',
        'product',
        'account',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_ddt_from_stock_wizard.xml',
        'views/stock_picking_type.xml',
        'views/stock_picking.xml',
        'views/l10n_it_ddt.xml'
    ],
    'auto_install': True,
}
