# -*- coding: utf-8 -*-
{
    'name': "ISA Extension: Analytic Accounting",

    'summary': """
         This module introduces enhancement for the analytic module """,

    'description': """
        This module introduces enhancement for the analytic module
    """,

    'author': "ISA S.r.L.",
    'website': "https://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.0.0.3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'analytic',
    ],

    'data': [
        'views/account_account.xml',
        'views/account_analytic_account.xml',
        'views/account_move.xml',
        'views/account_analytic_line.xml'
    ],
}
