# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Bank Papers ",

    'summary': """
        This modules introduces a the Italian management of Bank Paper.""",

    'description': """
        This modules introduces a the Italian management of Bank Paper.
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.0.1.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'payment_term_extension_isa',
        'account_extension_isa'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/select_bank_paper_slip_type_wizard.xml',
        'views/bank_papers_slip_types.xml',
        'views/l10n_it_bank_paper.xml',
        'views/l10n_it_bank_paper_slip.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/account_account.xml',
        'views/account_move_line.xml',
        'wizard/select_payment_type_wizard.xml',
        'wizard/l10n_it_bank_paper_slip_summary_wizard.xml',
        'wizard/file_export_wizard.xml',
        'views/menu_items.xml',
        'views/account_move.xml',
        'views/unsolved_template.xml',
        'report/report_bank_paper.xml'
    ],
}
