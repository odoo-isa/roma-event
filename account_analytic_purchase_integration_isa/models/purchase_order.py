# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        res = super(PurchaseOrder, self)._onchange_picking_type_id()
        if self.picking_type_id and self.picking_type_id.analytic_account_id:
            filtered_lines = self.order_line.filtered(lambda l: not l.account_analytic_id)
            for line in filtered_lines:
                line.account_analytic_id = self.picking_type_id.analytic_account_id.id
        return res