# -*- coding: utf-8 -*-
{
    'name': "Purchase Multiple Discount",

    'summary': """
        This module introduces three level of discount on purchase order line
    """,

    'description': """
        This module introduces three level of discount on purchase order line
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '13.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'purchase'],

    # always loaded
    'data': [
        'views/purchase_order_view.xml',
        'report/purchase_report_multiple_discount_template.xml'
    ]
}
