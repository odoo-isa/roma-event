# -*- coding: utf-8 -*-
{
    'name': "ISA Extension: Sale",
    'summary': """
    This module enable barcode feature for the sale order 
""",

    'description': """
    This module enable barcode feature for the sale order document
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'barcodes',
    ],

    # always load
    'data': [
        'views/sale_order.xml'
    ]
}
