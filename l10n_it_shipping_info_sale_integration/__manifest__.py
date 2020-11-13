# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Shipping Info Sale Integration",

    'summary': """
        Provide some basic shipping info on Sale Orders:
        - Goods Description
        - Transportation Reason
        - Trasportation Method
        - Incoterm
        """,

    'description': """
        This module adds some shipping's info on sale orders
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
        'sale',
        'l10n_it_shipping_info',
    ],

    # always loaded
    'data': [
        'views/sale_order.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
