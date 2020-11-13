# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.order_id.picking_type_id and self.order_id.picking_type_id.analytic_account_id and not self.account_analytic_id:
            self.account_analytic_id = self.order_id.picking_type_id.analytic_account_id.id
        return res
