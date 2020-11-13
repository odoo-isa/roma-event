# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = "product.category"

    preferential_tax_na = fields.Boolean(
        string='Preferential tax not applicable',
        help="If set, the system applies the tax associated to the product even if the SO delivery address provides a preferential tax.",
        copy=True
    )
