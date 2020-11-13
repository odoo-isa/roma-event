# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        res = super(PurchaseOrder, self)._onchange_picking_type_id()
        for order_line in self.order_line:
            order_line.warehouse_dest_id = None
        return res
