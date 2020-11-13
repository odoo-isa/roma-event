# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sp_account_id = fields.Many2one(
        string='Sp Account',
        comodel_name='account.account',
        related="company_id.sp_account_id",
        help="It shows account used in invoices with split payment, this account is in the move lines after invoice validation",
        readonly=False
    )