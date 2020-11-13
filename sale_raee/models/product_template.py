# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_applicable_waste_cost = fields.Boolean(
        string='Waste cost applicable',
        help="If selected, it shows that product is waste cost applicable",
        copy=True
    )

    waste_cost_amount = fields.Float(
        string='Waste cost amount',
        help="It shows amount of waste cost",
        copy=True
    )

    @api.onchange('is_applicable_waste_cost')
    def _onchange_is_waste_cost(self):
        self.waste_cost_amount = 0

    @api.constrains('is_applicable_waste_cost', 'waste_cost_amount')
    def _check_waste_amount(self):
        if self.is_applicable_waste_cost and self.waste_cost_amount <= 0 and self.product_variant_id.waste_cost_amount <= 0:
            raise ValidationError(_("Insert waste cost amount"))
