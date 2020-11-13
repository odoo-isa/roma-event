# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class L10NItDdTLine(models.Model):
    _inherit = 'l10n_it.ddt.line'

    stock_move_id = fields.Many2one(
        string='Stock move line',
        comodel_name='stock.move',
        ondelete="restrict",
        help="Link this ddt line to stock move",
        copy=False,
    )

    @api.model
    def _compute_quantity_to_invoice(self, precision):
        """
        Inherited function to determinate the quantity to invoice
        :param precision: the precision digits
        :return: quntity to invoice (float)
        """
        quantity = super(L10NItDdTLine, self)._compute_quantity_to_invoice(precision)
        # Remove quantity from return mve to refund
        move_return = self.env['stock.move'].search([
            ('origin_returned_move_id', '=', self.stock_move_id.id),
            ('to_refund', '=', True)
        ])
        if move_return:
            quantity -= sum([x.product_qty for x in move_return])
        return quantity
