# -*- coding: utf-8 -*-
{
    'name': "ISA Localization for Italy: Account Withholding Tax",

    'summary': """
        This module introduces the management of account withholding tax on customer/supplier invoice""",

    'description': """
Quickstart
===========
Guida di configurazione rapida. Per poter funzionare correttamente, questo modulo ha bisogno
di alcune configurazioni.

Impostazioni sui conti contabili
**********************************

All'interno dei conti contabili utilizzati per le ritenute deve essere impostato il campo 
*Uso (Usage)* con il valore *Ritenuta d'acconto (Withholding tax)*.

Impostazioni delle imposte
*****************************

Le ritenute di acconto, non sono altro che delle imposte. Il modulo precarica le principali:

    * 1038 **Provvigioni per rapporti di agenzia di mediazione e di rappresentanza**
    
    * 1040 **Lavoro autonomo: arti e professioni**
    
    * 1043 **Lav.autonomo: sogg. Esteri**
    
La configurazione di queste ritenute deve essere completata aggiungendo:

    1. Il conto contabile (che deve avere il campo *Uso* impostato con *Ritenuta d'acconto*) all'interno della sezione *ripartizione per fatture*

    2. La causale di pagamento, come riportata da modello 770S  (all'interno del tab *Opzioni Avanzate*)
    
    3. Il conto transitorio per le ritenute (che deve avere il campo *Uso* impostato con *Ritenuta d'acconto*, all'interno del tab *Opzioni Avanzate*) 

Creazione di una nuova ritenuta in anagrafica
************************************************

Per creare una nuova ritenute è necessario creare una nuova imposta.
I campi ai quali deve essere prestata particolare attenzione sono:

    1. *Importo*, deve essere settato con valore negativo (Esempio -20,0000%)

    2. Il conto contabile sulle righe di *Ripartizione per fatture* (che deve avere il campo *Uso* impostato con *Ritenuta d'acconto*)

All'interno del tab *Opzioni Avanzate*:

    1. Il campo *Addebito imposta* deve essere *Basato su pagamento*
    
    2. Il campo *Causale pagamento* deve essere conforme al modello 770S
    
    3. Il campo *Conto transitorio* (che deve avere il campo *Uso* impostato con *Ritenuta d'acconto*)
    
**Non dimenticarsi di impostare i gruppi di imposta con ritenuta d'acconto**
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.0.2.1',
    'maintainer': 'For Fee',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_setup',
        'account',
        'l10n_it',
        'web',
        'account_patch_isa',
        'account_extension_isa',
        'l10n_it_edi',
        'l10n_it_edi_extension_isa',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/import_account_tax.xml',
        'data/ir_sequence.xml',
        'data/invoice_it_template.xml',
        'wizard/payment_withholding_tax_wizard.xml',
        'views/res_config_settings.xml',
        'views/res_partner_view.xml',
        'views/account_tax.xml',
        'views/account_move_line.xml',
        'views/l10n_it_payment_withholding_tax.xml',
        'views/menuitem.xml',
    ],
}