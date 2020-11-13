# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Products Unique Internal Reference',
    'version': '13.0.1.0.7',
    'category': 'Tools',
    'description': """

    New Features:
    
    This module:
    * Creates a sequence that will be used to assign relating product's internal reference
    * Assigns internal reference for products that are set as active
    * Products can also be filtered for supplier code
    
    * An e-mail is sent to the set address containing link to confirm it. If so, it's validated in Odoo
    """,
    'depends': [
        'base',
        'product',
        'purchase'
    ],
    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",
    'data': [
        'data/sequence.xml',
        'views/product_template_views.xml',
        'views/product_views.xml'
    ],
}
