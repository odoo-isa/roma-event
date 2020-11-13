# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models
from logging import getLogger

_logger = getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """ Adding shipment info if move come from sale.order """
        res = super(StockMove, self)._get_new_picking_values()
        if self.sale_line_id:
            order_id = self.sale_line_id.order_id
            res.update({
                'goods_description_id': order_id.goods_description_id.id,
                'transportation_method_id': order_id.transportation_method_id.id,
                'transportation_reason_id': order_id.transportation_reason_id.id,
                'incoterm_id': order_id.incoterm.id
            })
        return res
