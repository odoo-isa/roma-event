# -*- coding: utf-8 -*-
{
    'name': "Account favourite billing method",

    'summary': """
        This module adds billing method in partner    
    """,

    'description': """
        This module adds billing method in partner
    """,

    'author': "ISA S.r.L.",
    'website': "https://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'l10n_it_ddt_extension_isa',
                'l10n_it_accompanying_invoice'],

    # always loaded
    'data': [
        'views/res_partner_view.xml'
    ]
}
