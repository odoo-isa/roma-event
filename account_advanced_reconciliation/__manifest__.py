# -*- coding: utf-8 -*-
{
    'name': "Advanced Accounting Reconciliation",

    'summary': """
        Manage the account book and the moves reconciliation""",

    'description': """
        Manage the account book and the moves reconciliation
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.1.0.5',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account'
    ],

    # always loaded
    'data': [
        'views/account_move.xml',
        'views/res_config_settings.xml',
    ],
}
