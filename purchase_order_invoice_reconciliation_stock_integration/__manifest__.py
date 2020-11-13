# -*- coding: utf-8 -*-
{
    'name': "Purchase Order/Invoice Reconciliation and Stock Integration",

    'summary': """
        Technical integration model between purchase_order_invoice_reconciliation and stock""",

    'description': """
        Technical integration model between purchase_order_invoice_reconciliation and stock
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '13.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'purchase_order_invoice_reconciliation',
        'stock',
        'purchase_stock',
    ],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/stock_picking.xml',
        'views/order_line_reconcile.xml',
    ],
    'auto_install': True,
}
