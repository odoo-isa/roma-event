# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Accounting Entry Management",

    'summary': """
        This modules introduces a the Italian management of Accounting Entry.""",

    'description': """
        This modules introduces a the Italian management of Accounting Entry.
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.0.2.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'product',
        'account_advanced_reconciliation'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/accounting_entry_security.xml',
        'views/account_account.xml',
        'views/account_move.xml',
        'views/l10n_it_accounting_entry.xml',
        'views/account_payment.xml',
        'wizard/l10n_it_accounting_entry_merge_split.xml',
        'wizard/wizard_report_accounting_entry_view.xml',
        'report/report_accounting_entry.xml',
        'views/menuitem.xml'
    ],
    'post_init_hook': '_setup_account_entry_flag_on_account',
}
