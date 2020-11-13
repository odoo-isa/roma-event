# -*- coding: utf-8 -*-
{
    'name': "ISA Extension: Base",

    'summary': """
        Provide some basic functionalities:
        - A default modules filter to get all modules developed by ISA S.r.L.
        - The translation for all the modules developed by ISA S.r.L.
    """,

    'description': """
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Rights',
    'version': '13.0.1.0.11',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'sale'
    ],
    'data': [
        'i18n/init.xml',
        'views/sale_order.xml'
    ]
}
