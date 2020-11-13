# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Government Invoicing",

    'summary': """
        This module manages public administration invoice account localized in Italy    
    """,

    'description': """
        This module manages public administration invoice account localized in Italy
    """,

    'author': "ISA S.r.L.",
    'website': "https://isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.1.0.6',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'sale',
                'account',
                'l10n_it_edi_extension_isa'],

    # always loaded
    'data': [
        'views/res_partner_view.xml'
    ]
}
