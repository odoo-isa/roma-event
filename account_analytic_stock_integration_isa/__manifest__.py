# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account Analytic and Stock Integration',
    'version': '13.0.0.0.2',
    'summary': 'Create Account Analytic Line Based on Stock Move',
    'author': 'ISA S.r.L.',
    'description': "This module is to create account analytic line with source location and destination location "
                   "based on stock move.",
    'category': 'Inventory',
    'depends': ['stock_account'],
    'data': [
        'views/stock_location_views.xml',
        'views/account_analytic_line_view.xml',

        'wizard/stock_analytic_items_wizard.xml',
    ],
    'installable': True,
    'application': False,
}
