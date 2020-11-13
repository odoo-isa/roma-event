# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Advanced E-Invoicing",

    'summary': """
        This module extends the Odoo out of the box Italian electronic invoicing features.""",

    'description': """
        This module extends the Odoo out of the box Italian electronic invoicing features.
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.3.3',
    'maintainer': 'For Fee',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_extension_isa',
        'account_patch_isa',
        'l10n_it',
        'l10n_it_edi',
        'payment_term_extension_isa',
        'notify_message'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_backend.xml',
        'views/res_config_settings.xml',
        'views/account_move.xml',
        'views/payment_type.xml',
        'views/account_tax.xml',
        "data/invoice_it_template.xml",
        'wizard/account_invoice_import_wizard_view.xml',
        'views/res_partner.xml'
    ],
    'qweb': [
        'static/src/xml/bills_tree_upload.xml',
    ],
}
