# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    invoice_purchase_order_line_reconcile_ids = fields.One2many(
        string='Invoice Order Line Reconciled',
        comodel_name='invoice.purchase.order.line.reconcile',
        inverse_name='purchase_order_line_id',
        help="Already reconciled lines",
        copy=False
    )

    @api.depends('invoice_purchase_order_line_reconcile_ids')
    def _compute_qty_invoiced(self):
        super(PurchaseOrderLine, self)._compute_qty_invoiced()
        for line in self:
            line.qty_invoiced += sum(line.mapped('invoice_purchase_order_line_reconcile_ids.qty'))
