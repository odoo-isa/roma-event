# -*- coding: utf-8 -*-
{
    'name': "ISA Patch: Accounting",

    'summary': """
        This module introduces some fix on Odoo standard account management.""",

    'description': """
        This module introduces some fix on Odoo standard account management.
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.1.2.4',
    'maintainer': 'For Fee',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account'
    ],

    # always loaded
    'data': [
        'views/account_move.xml'
    ]
}
