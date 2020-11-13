# -*- coding: utf-8 -*-
{
    'name': "Account Invoice Change Due Date",

    'summary': """
         This module introduces possibility to change due date in customer invoices """,

    'description': """
         This module introduces possibility to change due date in customer invoices
    """,

    'author': "ISA S.r.L.",
    'website': "https://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.0.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_accountant',
        'account_advanced_reconciliation',
        'payment_term_extension_isa'
    ],

    # always loaded
    'data': [
        'wizard/account_move_line_change_due_date_wizard.xml',
        'views/account_move.xml',
        'wizard/account_due_date_wizard.xml'

    ],
}
