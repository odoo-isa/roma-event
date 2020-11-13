# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Shipping Info Stock Integration",

    'summary': """
        Provide some basic shipping info on Pickings:
        - Goods Description
        - Transportation Reason
        - Trasportation Method
        - Incoterm
        """,

    'description': """
        This module adds some shipping's info on pickings
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'stock',
        'l10n_it_shipping_info',
    ],

    # always loaded
    'data': [
        'views/stock_picking.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
