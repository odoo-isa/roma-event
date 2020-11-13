# -*- coding: utf-8 -*-
{
    'name': "Italian Cash Register Interface",

    'summary': """
        Italian cash register interface""",

    'description': """
        Italian cash register interface 
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    'category': 'Hidden',
    'version': '13.0.0.0.1',

    'depends': [
        'base',
        'web',
        'sale',
        'hr',
        'account',
        'sale_management',
        'iot',
        'account_extension_isa',
        'payment_term_extension_isa',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/sale_print_bill.xml',
        'views/iot_box.xml',
        'views/hr_department.xml',
        'views/cash_template.xml',
        'views/payment_type.xml',
        'views/res_users.xml',
        'views/account_tax.xml',
    ],

    'qweb': [
        'static/src/xml/*.xml',
    ],

    'installable': True,

}
