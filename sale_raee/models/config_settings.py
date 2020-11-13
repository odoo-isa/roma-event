# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    waste_cost_id = fields.Many2one(
        string='Waste cost',
        comodel_name='product.product',
        readonly=False,
        related="company_id.waste_cost_id",
        help="It indicates for what product must be computed waste cost",
        copy=False
    )
