# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    set_extra_max_discount = fields.Boolean(
        string='Set Extra Max Discount',
        help='If true, it allows you to set the maximum extra discount',
    )

    extra_max_discount = fields.Float(
        string='Extra Max Discount',
        help='Extra maximum discount allowed for the counter user'
    )

    @api.onchange('set_extra_max_discount')
    def onchange_product_category(self):
        if not self.set_extra_max_discount:
            self.extra_max_discount = 0.0




