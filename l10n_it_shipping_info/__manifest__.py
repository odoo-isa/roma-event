# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Shipping Info",

    'summary': """
        Provide some basic shipping info on Partners:
        - Goods Description
        - Transportation Reason
        - Trasportation Method
        - Incoterm
        """,

    'description': """
        This module adds some shipping's info on partners
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.0.0.5',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account'
    ],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
