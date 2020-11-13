# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    split_payment = fields.Boolean(
        string='Split Payment',
        help="If it's active, invoices with this account fiscal position use split payment",
        copy=False
    )
