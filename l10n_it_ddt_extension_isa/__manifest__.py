# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Delivery Note",

    'summary': """
        ISA Localization for Italy: Delivery Note
        """,

    'description': """
        This module adds add new attributes and features to Transport Document
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.3.5',
    'maintainer': 'For Fee',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'account',
        'l10n_it_edi',
        'l10n_it_edi_extension_isa',
        'l10n_it_shipping_info',
        'notify_message',
        'account_patch_isa'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/l10n_it_ddt_template.xml',
        'wizard/ddt_advance_payment_invoice.xml',
        'views/l10n_it_ddt.xml',
        'views/product_template.xml',
        'views/account_move.xml',
        'views/l10n_it_ddt_extension_isa_menu.xml',
        'data/l10n_it_ddt_extension_isa_data.xml',
        'views/ddt_report.xml',
        'views/ddt_enhanced_report.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}