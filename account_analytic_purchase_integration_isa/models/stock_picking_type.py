# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    analytic_account_id = fields.Many2one(
        string='Analytic Account',
        required=False,
        readonly=False,
        comodel_name='account.analytic.account',
        help='',
        copy=False,
    )




