# -*- coding: utf-8 -*-
{
    'name': "Sale RAEE",

    'summary': """
        This module manages waste cost contribution
    """,

    'description': """
        This module manages waste cost contribution adding product to choice in configuration and filling up automatically waste cost lines in sale order
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '13.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'sale',
                'sale_management'],

    # always loaded
    'data': [
        'views/product_template_view.xml',
        'views/config_settings_view.xml',
        'views/waste_cost_view.xml',
        'views/sale_order_view.xml',
    ]
}
