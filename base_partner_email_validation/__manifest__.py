# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Partner Email Validation',
    'version': '13.0.1.0.7',
    'category': 'Tools'
                '',
    'description': """

    New Features:
    
    This module allows you to validate email that is entered on the contacts.
    
    * An e-mail is sent to the set address containing link to confirm it. If so, it's validated in Odoo
    """,
    'depends': [
        'base',
        'mail',
        'auth_signup',
        'purchase'
    ],
    'author': "ISA S.r.L.",
    'website': "https://www.isa.it/blog/il-nostro-blog-1/post/validazione-email-del-partner-9",
    'data': [
        'views/assets.xml',
        'data/mail_template_data.xml',
        'views/confirm_mail_templates.xml',
        'views/res_partner_view.xml'
    ],
}
