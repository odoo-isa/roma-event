# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields
from logging import getLogger

_logger = getLogger(__name__)


class StockMoveQuantityOwnerInfo(models.Model):
    _inherit = 'stock.move.quantity.owner.info'

    purchase_line_id = fields.Many2one(
        string='Purchase Line',
        required=False,
        readonly=False,
        comodel_name='purchase.order.line'
    )
