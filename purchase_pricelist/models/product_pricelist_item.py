# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, _
from logging import getLogger
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    def unlink(self):
        supplierinfo_row_obj = self.env['product.supplierinfo'].search([('product_pricelist_item_id', 'in', self.ids)])
        if supplierinfo_row_obj:
            raise UserError(_("You cannot delete an Item linked to supplierinfo row."))
        return super(ProductPricelistItem, self).unlink()
