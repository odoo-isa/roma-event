# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_not_invoiced = fields.Monetary(
        string='Amount not Invoiced',
        default=0.0,
        compute='_compute_amount_not_invoiced',
        help=False
    )

    @api.depends('order_line')
    def _compute_amount_not_invoiced(self):
        for order in self:
            amount_invoiced = 0.0
            # I used qty_invoiced because qty_to_invoice is not always compute
            for line in order.order_line:
                price_dict = line.tax_id.compute_all(line.price_unit, line.order_id.currency_id, line.qty_invoiced,
                                        product=line.product_id, partner=line.order_id.partner_id)
                amount_invoiced += price_dict['total_included']
            order.amount_not_invoiced = order.amount_total - amount_invoiced


