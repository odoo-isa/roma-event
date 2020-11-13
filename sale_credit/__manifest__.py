# -*- coding: utf-8 -*-
{
    'name': "Sale Credit",

    'summary': """
        Credit limit management for customers""",

    'description': """
        Credit limit management for customers 
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    'category': 'Sale',
    'version': '13.0.1.0.6',

    'depends': [
        'base',
        'account',
        'sale',
        'base_extension_isa'
    ],

    'data': [
        'views/res_partner.xml',
    ],
}
