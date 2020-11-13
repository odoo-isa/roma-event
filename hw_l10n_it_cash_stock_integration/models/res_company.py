# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    cash_register_force_reserve = fields.Boolean(
        string='Force Picking reservation on counter sales',
        help='''If enable this flag, the picking will be confirmed regardless the availability of goods during the 
        sale's counter.''',
    )
