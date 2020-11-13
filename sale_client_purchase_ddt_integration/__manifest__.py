# -*- coding: utf-8 -*-
{
    'name': "Sale Client Purchase Order and Delivery Note Integration",

    'summary': """
        This module introduces possibility to automatically creation of related documents in invoice from
        client purchase order of DDT and creation of client purchase order in DDT from sale order   
    """,

    'description': """
        This module introduces possibility to automatically creation of related documents in invoice from
        client purchase order of DDT and creation of client purchase order in DDT from sale order
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'DDT',
    'version': '13.0.1.0.4',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'sale_client_purchase_order',
                'l10n_it_ddt_extension_isa',
                'l10n_it_ddt_sale_integration'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/l10n_it_ddt_view.xml',
        'report/ddt_report.xml'
    ],
    'auto_install': True
}
