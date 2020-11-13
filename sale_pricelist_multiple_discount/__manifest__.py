# -*- coding: utf-8 -*-
{
    'name': "Sale Pricelist Multiple Discount",

    'summary': """
        This module introduces three level of discount on product pricelist item
    """,

    'description': """
        This module introduces three level of discount on product pricelist item
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Product',
    'version': '13.0.1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'product'],

    # always loaded
    'data': [
        'views/account_move_view.xml',
        'views/product_pricelist_item_view.xml',
        'report/invoice_report_multiple_discount_template.xml'
    ]
}
