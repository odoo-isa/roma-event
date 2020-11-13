# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Purchases Team',
    'version': '13.0.1.0.5',
    'category': 'Tools'
                '',
    'description': """

    New Features:
    
    In purchasing's configuration, a new basic group has been added to allow the management of its purchase orders
    
    """,
    'depends': [
        'base',
        'account',
        'purchase'
    ],
    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",
    'data': [
        'security/security.xml',
        'views/res_partner.xml',
        'views/purchase_order.xml'
    ],
}
