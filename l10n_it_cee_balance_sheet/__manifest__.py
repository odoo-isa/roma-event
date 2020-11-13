# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: CEE Balance Sheet",

    'summary': """
""",

    'description': """
""",

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.0.4',
    'maintainer': '',

    # any module necessary for this one to work correctly
    'depends': [
        'account_patch_isa',
        'account_extension_isa',
        'account_reports_extension_isa'
    ],

    # always loaded
    'data': [
        'data/cee_balance_sheet.xml',
        'data/cee_profit_and_loss.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}