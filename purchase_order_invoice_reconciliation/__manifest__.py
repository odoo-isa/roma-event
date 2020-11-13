# -*- coding: utf-8 -*-
{
    'name': "Purchase Order/Invoice Reconciliation",

    'summary': """
        This module provide a simple way to reconcile supplier invoices with purchase order""",

    'description': """
        This module provide a simple way to reconcile supplier invoices with purchase order
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '13.0.2.0.4',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'purchase',
        'product',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/assets.xml',
        'views/order_line_reconcile.xml',
        'views/purchase_order.xml',
        'wizard/unbalance_reconciliation_reason_wizard.xml',
    ],
    'qweb': [
        'static/src/xml/invoice_purchase_order_line_reconcile.xml'
    ],
}
