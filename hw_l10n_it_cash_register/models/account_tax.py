# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    cash_department = fields.Integer(
        string='Cash register department',
        help='The configured department from the cash register configuration',
        copy=False,
    )
