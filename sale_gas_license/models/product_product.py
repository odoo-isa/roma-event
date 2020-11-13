# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    contains_gas = fields.Boolean(
        string='Contains Gas',
        help='This product contains Gas',
        store=True,
        compute='_get_contains_gas',
        inverse='_set_contains_gas'
    )

    @api.depends('product_tmpl_id')
    def _get_contains_gas(self):
        for variant in self:
            variant.contains_gas = variant.product_tmpl_id.contains_gas

    def _set_contains_gas(self):
        pass

