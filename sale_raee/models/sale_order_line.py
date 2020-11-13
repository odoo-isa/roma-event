# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_waste_cost = fields.Boolean(
        string='Waste cost',
        help="It indicates if order line is waste applicable",
        copy=True
    )

    link_with_raee = fields.Many2one(
        string='Link with Raee',
        help="If the line of order have a waste cost, this fields value as id of product with waste cost ",
        comodel_name='sale.order.line',
    )
