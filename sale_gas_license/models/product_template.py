# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    contains_gas = fields.Boolean(
        string='Contains Gas',
        help='This product contains Gas',
        store=True,
    )

    @api.onchange('type', 'contains_gas')
    def _onchange_contains_gas(self):
        if self.type in ['service']:
            self.contains_gas = False

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'contains_gas' in vals:
            if len(self.attribute_line_ids) == 0 and len(self.product_variant_ids) == 1:
                self.product_variant_ids.contains_gas = self.contains_gas
        return res