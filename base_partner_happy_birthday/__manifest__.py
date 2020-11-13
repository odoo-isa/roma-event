{
    'name': "Partner Happy Birthday",
    'version': '13.0.1.0.1',
    'depends': [
        'base',
        'mail'
    ],
    'author': "ISA S.r.L.",
    'category': 'Tool',
    'description': """
    This module introduces date of birth in the partners. A scheduled action will send a greeting email on the birthday
    """,
    'data': [
        'views/res_partner.xml',
        'data/email_template.xml',
        'data/ir_cron_data.xml'
    ],
}