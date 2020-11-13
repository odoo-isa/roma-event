# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Split Payment",

    'summary': """
        Module to generate Split Payment accounting entries.
    """,

    'description': """
        This module introduces functionalities and corrections concerning the management of Accounting in Odoo.
        In particular it adds in accounting section of configurations, the possibility to choice an account for split playment.
        During creation of an invoice, user can activate split payment option in fiscal position, achievable directly from invoice form.
        If split payment is active, after invoice validation, journal entry will show other account move lines with the configuration account in settings.
        In this case products price in account move line will be untaxed, because amount tax is visible in the line of split payment.
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '13.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_patch_isa',
        'l10n_it_edi'
    ],

    # always loaded
    'data': [
        'views/res_config_settings.xml',
        'views/account_fiscal_position.xml',
        'views/account_move.xml',
        'data/account_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}