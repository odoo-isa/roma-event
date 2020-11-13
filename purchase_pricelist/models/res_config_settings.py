# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    update_sale_pricelist = fields.Boolean(
        string='Update sale pricelist',
        related="company_id.update_sale_pricelist",
        readonly=False,
        help="",
        copy=False
    )
