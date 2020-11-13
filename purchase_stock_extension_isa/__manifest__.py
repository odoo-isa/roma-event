# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Purchase Stock Extension Isa",
    'version': '13.0.1.0.0',
    'category': 'Operations/Purchase',
    'summary': "Manage Purchase Order by Sale Order",
    'description': """
        """,
    'depends': [
        'purchase_stock',
        'stock_extension_isa'
    ],
    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",
    'data': [
        'views/purchase_order.xml'
    ],
}
