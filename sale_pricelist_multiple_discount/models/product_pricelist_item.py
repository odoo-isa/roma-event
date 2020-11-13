# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    discount1 = fields.Float(
        string="First Discount",
        digits='Discount'
    )

    discount2 = fields.Float(
        string="Second Discount",
        digits='Discount'
    )

    discount3 = fields.Float(
        string="Third Discount",
        digits='Discount'
    )

    price_discount = fields.Float(
        readonly=True
    )

    @api.onchange('discount1', 'discount2', 'discount3')
    def _compute_max_discount(self):
        discount1 = 100 - self.discount1
        discount2 = 100 - self.discount2
        discount3 = 100 - self.discount3
        if discount1 or discount2 or discount3:
            tot = 100 - (100 * (discount1 / 100) * (discount2 / 100) * (discount3 / 100))
            self.price_discount = tot

    def write(self, vals):
        res = True
        for record in self:
            discount1 = 100 - (vals.get('discount1') or record.discount1 or 0)
            discount2 = 100 - (vals.get('discount2') or record.discount2 or 0)
            discount3 = 100 - (vals.get('discount3') or record.discount3 or 0)
            if discount1 or discount2 or discount3:
                tot = 100 - (100 * (discount1 / 100) * (discount2 / 100) * (discount3 / 100))
                if tot:
                    vals['price_discount'] = tot
            res |= super(ProductPricelistItem, record).write(vals)
        return res

    @api.model
    def create(self, vals):
        discount1 = 100 - (vals.get('discount1') or self.discount1 or 0)
        discount2 = 100 - (vals.get('discount2') or self.discount2 or 0)
        discount3 = 100 - (vals.get('discount3') or self.discount3 or 0)
        if discount1 or discount2 or discount3:
            tot = 100 - (100 * (discount1 / 100) * (discount2 / 100) * (discount3 / 100))
            if tot:
                vals['price_discount'] = tot
        return super(ProductPricelistItem, self).create(vals)
