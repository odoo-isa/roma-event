# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Purchase Pricelist',
    'version': '13.0.1.1.8',
    'category': 'Tools'
                '',
    'description': """

    New Features:
    
    Il modulo permette di importare file csv utili ai listini di acquisto fornitore
    
    """,
    'depends': [
        'base',
        'account',
        'purchase',
        'web',
        'product',
        'stock_extension_isa'
    ],
    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",
    'data': [
        'data/pricelist_data.xml',
        'security/ir.model.access.csv',
        'views/product_supplier_family.xml',
        'wizard/supplierinfo_family_wizard.xml',
        'wizard/import_file_pricelists_wizard.xml',
        'views/menu_item.xml',
        'views/res_partner.xml',
        'views/product_supplierinfo.xml',
        'views/product_view.xml',
        'views/res_config_settings_view.xml'
    ],
}
