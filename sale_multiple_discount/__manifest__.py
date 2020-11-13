# -*- coding: utf-8 -*-
{
    'name': "Sale Multiple Discount",

    'summary': """
        This module introduces three level of discount on sale order line
    """,

    'description': """
        This module introduces three level of discount on sale order line
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '13.0.1.0.5',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'sale'],

    # always loaded
    'data': [
        'views/sale_order_view.xml',
        'views/product_category.xml',
        'report/sale_report_multiple_discount_template.xml'
    ]
}
