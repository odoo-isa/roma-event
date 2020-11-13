# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Preferential Tax",

    'summary': """
        This module introduces possibility to manage preferential tax for particular partner and product  
    """,

    'description': """
        This module introduces possibility to manage preferential tax for particular partner and product
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.0.11',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'product',
                'sale',
                'account'],

    # always loaded
    'data': [
        'data/account_preferential_tax_data.xml',
        'views/menuitem.xml',
        'security/ir.model.access.csv',
        'views/account_preferential_tax_type_view.xml',
        'views/account_preferential_tax_view.xml',
        'views/res_partner_view.xml',
        'views/product_template_view.xml',
        'views/product_category_view.xml',
        'report/report.xml',
        'report/template.xml',
        'report/report_invoice.xml'
    ]
}
