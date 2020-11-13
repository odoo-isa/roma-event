# -*- coding: utf-8 -*-
{
    'name': "Sale Client Purchase Order and Stock Integration",

    'summary': """
        This module allows to create client purchase order in DDT from stock picking  
    """,

    'description': """
        This module allows to create client purchase order in DDT from stock picking
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '13.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'sale_client_purchase_order',
                'l10n_it_ddt_stock_integration',
                'l10n_it_ddt_sale_stock_integration'],
    'auto_install': True
}
