# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    client_purchase_order_required = fields.Boolean(
        string='Client purchase order required',
        help="It shows if partner has to use client purchase order or not",
        copy=True
    )
