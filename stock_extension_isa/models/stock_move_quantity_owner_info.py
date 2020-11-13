# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class StockMoveQuantityOwnerInfo(models.Model):
    _name = 'stock.move.quantity.owner.info'
    _description = 'Information about owner of the goods'

    move_id = fields.Many2one(
        string='Move',
        comodel_name='stock.move',
        ondelete="cascade",
        help='Link with the move',
    )

    doc_reference = fields.Reference(
        string='Reference document',
        selection=[('sale.order', 'Sale Order')],
        help='Document for which the goods are reserved',
    )

    quantity = fields.Float(
        string='Reserved quantity',
        digits='Product Unit of Measure',
        help='Quantity reserved for owner',
        copy=False,
    )

    owner = fields.Many2one(
        string='Owner',
        comodel_name='res.partner',
        help='Partner owner',
        compute="_get_owner"
    )

    def _get_owner(self):
        for info in self:
            if hasattr(info.doc_reference, 'partner_id'):
                info.owner = getattr(info.doc_reference, 'partner_id').id
