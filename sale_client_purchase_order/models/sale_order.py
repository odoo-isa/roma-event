# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    client_purchase_order_ids = fields.One2many(
        string='Client purchase order',
        comodel_name='client.purchase.order',
        inverse_name='sale_order_id',
        help="List of client purchase order linked to sale order",
        copy=True
    )

    client_purchase_order_required_rel = fields.Boolean(
        string='Client purchase order required',
        related="partner_id.client_purchase_order_required",
        help="It indicates value of flag field of partner who has to use client purchase order or not",
        copy=False
    )

    @api.constrains('partner_id', 'client_purchase_order_ids')
    def _check_client_purchase(self):
        if self.partner_id.client_purchase_order_required and not self.client_purchase_order_ids:
            raise ValidationError(_("There's not link to coupon required to partner sale. Specify coupon in specific tab."))
