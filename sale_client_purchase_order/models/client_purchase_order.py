# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ClientPurchaseOrder(models.Model):
    _name = "client.purchase.order"
    _description = "Client Purchase Order"

    name = fields.Char(
        string='Name',
        required=True,
        help="Name of client purchase order",
        copy=True
    )

    date = fields.Date(
        string='Date',
        required=True,
        help="Date of client purchase order",
        copy=True
    )

    sale_order_id = fields.Many2one(
        string='Sale order',
        comodel_name='sale.order',
        help="Link to sale order",
        copy=True
    )
