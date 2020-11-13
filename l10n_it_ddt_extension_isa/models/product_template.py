# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    weight_net = fields.Float(
        string='Net Weight',
        digits='Product Price',
        help="The Net weight in Kg."
    )
