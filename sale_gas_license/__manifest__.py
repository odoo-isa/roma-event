# -*- coding: utf-8 -*-
{
    'name': "Sale F-Gas License",

    'summary': """
        This module manages the gas license
        """,

    'description': """
        This module manages the gas license
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    'category': 'Sale',
    'version': '13.0.1.0.4',

    'depends': ['base',
                'sale',
                'sale_management',
                'stock'],

    'data': [
        'views/res_partner.xml',
        'views/product_template.xml',
        'views/product_product.xml'
    ],

}
