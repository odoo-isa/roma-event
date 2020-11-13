# -*- coding: utf-8 -*-
{
    'name': "Partner Delegation",

    'summary': """
        This module introduces possibility to insert in partner his delegates for purchase or pick up goods
    """,

    'description': """
        This module introduces possibility to insert in partner his delegates for purchase or pick up goods
    """,

    'author': "ISA S.r.L.",
    'website': "https://www.isa.it/blog/il-nostro-blog-1/post/delega-per-il-contatto-10",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Partner',
    'version': '13.0.2.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/res_partner_delegation_view.xml',
        'report/report.xml',
        'report/template.xml'
    ]
}
