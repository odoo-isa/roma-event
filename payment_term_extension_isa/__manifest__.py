# -*- coding: utf-8 -*-
{
    'name': "ISA Extension: Payment Terms",

    'summary': """
        This module introduces payment's type management
    """,

    'description': """
        This module introduces payment's type management
    """,

    'author': "ISA S.r.L.",
    'website': "https://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.1.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'account_patch_isa'
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/payment_type_view.xml',
        'views/account_payment_term_line_view.xml',
        'views/account_move_view.xml',
        'views/account_move_line_view.xml'
    ]
}
