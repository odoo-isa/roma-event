# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account Analytic and Purchase Integration',
    'version': '13.0.0.0.2',
    'summary': 'Account Analytic and Purchase Integration',
    'author': 'ISA S.r.L.',
    'description': "",
    'category': 'Inventory',
    'depends': ['stock',
                'analytic',
                'purchase_stock',],
    'data': [
        'views/stock_picking_type.xml',
        'views/purchase_order.xml'
    ],
    'installable': True,
    'application': False,
}
