# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Tax Report",

    'summary': """
        ISA Localization for Italy: Management Journal Entry
        """,

    'description': """
    """,

    'author': "ISA S.r.L.",
    'website': "https://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.1.4',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_accountant',
        'account_extension_isa',
    ],

    # always loaded
    'data': [
        'data/account_tax_report_line_data.xml',
        'views/account_move.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ]
}
