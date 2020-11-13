# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Purchase Representative Substitutes",
    'version': '13.0.1.0.3',
    'category': 'Operations/Purchase',
    'summary': "Manage Purchase Order for Replacement Buyers",
    'description': """

    New Features:
    
    In purchasing's configuration, a new Purchase's Page has been added to allow the management purchase orders for
    Replacement Buyers

        """,
    'depends': [
        'account',
        'base',
        'purchase',
        'purchases_team'
    ],
    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",
    'data': [
        'security/purchase_security.xml',
        'views/res_partner.xml',
    ],
}
