# -*- coding: utf-8 -*-
{
    'name': "Sale no delivery cost",

    'summary': """
        This module introduces possibility to manage delivery cost, to set it optionally    
    """,

    'description': """
        This module introduces possibility to manage delivery cost, to set it optionally
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '13.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'delivery'],

    # always loaded
    'data': [
        'views/delivery_view.xml',
        'views/res_partner_view.xml'
    ]
}
