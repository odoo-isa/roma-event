# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Delivery Note and Sale Integration",

    'summary': """
        Integration between Ddt and sale module""",

    'description': """
        Integration between DdT and sale module.
    """,

    'author': "ISA S.r.L.",
    'website': "https://isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.0.9',

    # any module necessary for this one to work correctly
    'depends': [
        'l10n_it_ddt_extension_isa',
        'l10n_it_shipping_info_sale_integration',
        'sale',
        'product',
        'account',
    ],

    # always loaded
    'data': [
        'wizard/create_ddt_form_sale_wizard.xml',
        'wizard/ddt_advance_payment_invoice.xml',
        'views/sale_order.xml',
        'views/down_payment_template.xml',
        'views/l10n_it_ddt.xml'
    ],
    'auto_install': True,
}
