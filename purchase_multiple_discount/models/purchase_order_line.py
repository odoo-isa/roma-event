# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount = fields.Float(
        string='Discount %',
        digits='Discount'
    )

    discount1 = fields.Float(
        string='First Discount',
        digits='Discount'
    )

    discount2 = fields.Float(
        string='Second Discount',
        digits='Discount'
    )

    discount3 = fields.Float(
        string='Third Discount',
        digits='Discount'
    )

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount1', 'discount2', 'discount3')
    def _compute_amount(self):
        res = super(PurchaseOrderLine, self)._compute_amount()
        for record in self:
            discount1 = (100 - record.discount1) / 100
            discount2 = (100 - record.discount2) / 100
            discount3 = (100 - record.discount3) / 100
            tot = 100 - (100 * discount1 * discount2 * discount3)
            record.discount = tot
            record.price_subtotal = (record.price_unit - (record.discount * record.price_unit / 100)) * record.product_qty
            taxes = record.taxes_id.compute_all(
                record.price_subtotal,
                record.currency_id,
                1.0,
                record.product_id,
                record.partner_id)
            record.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            })


        return res
