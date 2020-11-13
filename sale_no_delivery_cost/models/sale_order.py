# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rel_not_delivery_outgoing = fields.Boolean(
        related="partner_id.not_delivery_outgoing",
        help="It set invisible button to add delivery in sale order"
    )
