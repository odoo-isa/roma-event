# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Accompanying Invoice",

    'summary': """
        ISA Localization for Italy: Accompanying Invoice
        """,

    'description': """
        This module adds new invoice's type: accompanying invoice
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.0.0.5',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'base',
        'sale',
        'account_patch_isa',
        'l10n_it_shipping_info'
    ],

    # always loaded
    'data': [
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/report_invoice.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}