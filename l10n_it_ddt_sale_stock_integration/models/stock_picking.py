# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    weight_net = fields.Float(
        string='Weight Net',
        compute='_cal_weight_net',
        digits='Stock Weight',
        store=True
    )

    @api.depends('move_lines')
    def _cal_weight_net(self):
        for picking in self:
            picking.weight_net = sum(move.weight_net for move in picking.move_lines if move.state != 'cancel')

    def prepare_ddt_values(self):
        """
        From picking create values for create ddt header.
        :return: dictionary of values
        """
        self.ensure_one()
        vals = super(StockPicking, self).prepare_ddt_values()
        # Retrieve the sale order values
        order = self.sale_id
        if order:
            vals.update({
                'partner_id': order.partner_invoice_id.id,
                'payment_term_id': order.payment_term_id.id,
                'weight_net': sum(self.mapped('weight_net')),
                'weight': sum(self.mapped('weight')),
                'carrier_id': self.carrier_id.id
            })
        return vals
