# -*- coding: utf-8 -*-
{
    'name': "ISA Extension: Account Reports",

    'summary': """Introduce alcuni miglioramenti a livello di usabilità utente per la definizione dei resoconti finanziari.""",

    'description': """Introduce alcuni miglioramenti a livello di usabilità utente per la definizione dei resoconti finanziari.\n
Permette di:\n
\u2022 Associare uno o più conti contabili alle sezioni dei report finanziari in modalità singola senza dover utilizzare l’approccio di definizione di un dominio.\n
\u2022 Associare conti analitici a conti contabili al fine di semplificare la generazione di movimenti di contabilità analitica contestuale a quella di movimenti contabili.
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.0.3.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account_reports',
        'account_accountant',
        'account',
    ],

    # always loaded
    'data': [
        'views/account_financial_html_report_line.xml',
        'views/account_account.xml',
    ],
}
