# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    withholding_tax_id = fields.Many2one(
        string='Withholding tax',
        comodel_name='account.tax',
        domain=[('account_tax_type', '=', 'withholding_tax')],
        help="",
        copy=True
    )