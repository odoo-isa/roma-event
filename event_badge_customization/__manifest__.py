# -*- coding: utf-8 -*-
{
    'name': "Event Badge Customization",

    'summary': """
        This module introduces customization on badge report""",

    'description': """
        This module introduces customization on badge report
    """,

    'author': "ISA S.r.L.",
    'website': "http://www.isa.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing/Events',
    'version': '13.0.1.0.0',
    'maintainer': 'For Fee',

    # any module necessary for this one to work correctly
    'depends': [
        'event',
    ],

    # always loaded
    'data': [
        'report/event_event_template.xml'
    ]
}