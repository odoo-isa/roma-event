# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Advanced MTO',
    'version': '13.0.2.0.2',
    'author': 'ISA S.r.L.',
    'category': 'Sales/Sales',
    'description': """
    
    New Features:
    This module manages transfer and receipt warehouse's goods on sales order
    
    """,
    'depends': [
        'sale',
        'purchase',
        'sale_management',
        'purchase_stock',
        'stock',
        'sale_stock',
        'stock_extension_isa',
        'uom',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_warehouse.xml',
        'views/stock_location_route.xml',
        'views/sale_order.xml',
        'views/asset.xml',
        'views/purchase_order.xml'
    ],
    'qweb': [
        'static/src/xml/qty_at_date.xml'
    ],
    'installable': True,
    'auto_install': False,
    'post_init_hook': '_update_warehouse_transit_location_and_buy_for_sold_route',
}
