# -*- coding: utf-8 -*-
{
    'name': "Sale Client Purchase Order",

    'summary': """
        This module introduces client purchase orders for specific partner in sale order
    """,

    'description': """
        This module introduces client purchase orders for specific partner in sale order and their rewrite in invoice
        which is created from sale order.
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '13.0.1.1.3',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'sale',
                'account',
                'l10n_it_edi_extension_isa'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/sale_report_template.xml',
        'report/invoice_report_template.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/client_purchase_order_view.xml'
    ]
}
