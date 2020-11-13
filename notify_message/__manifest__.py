# -*- coding: utf-8 -*-
{
    'name': "Notify Message",

    'summary': """
        This module presents the possibility to display a message for the user
""",

    'description': """
        This module presents the possibility to display a message for the user
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'wizard/notify_message_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}