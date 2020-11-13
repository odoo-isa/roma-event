# -*- coding: utf-8 -*-
{
    'name': "Integration between stock and cash register HW",

    'summary': """
        This module integrate the cash register for italian localization and the odoo stock module""",

    'description': """
        This module integrate the cash register for italian localization and the odoo stock module
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '13.0.0.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'hw_l10n_it_cash_register',
        'stock',
        'web',
    ],

    # always loaded
    'data': [
        'views/res_config_settings.xml',
        'views/assets.xml',
    ],
    'auto_install': True,
}
