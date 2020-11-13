# -*- coding: utf-8 -*-
{
    'name': "ISA Extension: Account",

    'summary': """
         This module introduces enhancement for the account module """,

    'description': """
        This module introduces enhancement for the account module
    """,

    'author': "ISA S.r.L.",
    'website': "https://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.0.1.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_accountant',
    ],

    # always loaded
    'data': [
        'views/account_group.xml',
        'views/account_move_line.xml',
        'views/account_move.xml',
        'views/account_account.xml',
        'views/res_partner_bank.xml'
    ],
}