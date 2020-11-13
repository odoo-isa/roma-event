# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    payment_type_id = fields.Many2one(
        string='Payment Type',
        readonly=True,
        comodel_name='payment.type',
        ondelete='set null',
        help="Indicates payment's type that will be used",
        copy=False
    )

    account_type = fields.Selection(
        string='Account Type',
        readonly=True,
        store=True,
        related='account_id.user_type_id.type',
        help="Related field to type ",
        copy=False
    )
