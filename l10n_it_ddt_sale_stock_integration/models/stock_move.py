# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    weight_net = fields.Float(
        string="Weight Net",
        compute='_cal_move_weight_net',
        digits='Stock Weight',
        store=True
    )

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _cal_move_weight_net(self):
        for move in self.filtered(lambda moves: moves.product_id.weight_net > 0.00):
            move.weight_net = (move.product_qty * move.product_id.weight_net)

    @api.model
    def prepare_ddt_values(self, quantity, partner_type='customer'):
        self.ensure_one()
        vals = super(StockMove, self).prepare_ddt_values(quantity, partner_type)
        order_line = self.sale_line_id
        if order_line:
            vals.update({
                'ddt_line_tax_ids': [(6, 0, order_line.tax_id.ids)],
                'price_unit': order_line.price_unit,
                'sale_order_line_id': order_line.id,
                'discount': order_line.discount
            })
        return vals
