# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount1 = fields.Float(
        string="First Discount %",
        digits='Discount'
    )

    discount2 = fields.Float(
        string="Second Discount %",
        digits='Discount'
    )

    discount3 = fields.Float(
        string="Third Discount %",
        digits='Discount'
    )

    @api.onchange('discount1', 'discount2', 'discount3', 'price_unit')
    def _compute_max_discount(self):
        discount1 = 100 - self.discount1
        discount2 = 100 - self.discount2
        discount3 = 100 - self.discount3
        tot = 100 - (100 * (discount1 / 100) * (discount2 / 100) * (discount3 / 100))
        self.discount = tot
