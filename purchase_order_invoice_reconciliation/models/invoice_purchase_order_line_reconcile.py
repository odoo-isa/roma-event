# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import fields, models


class InvoicePurchaseOrderLineReconcile(models.Model):
    _name = "invoice.purchase.order.line.reconcile"
    _description = "Reconciliation between purchase order line and invoice"

    invoice_id = fields.Many2one(
        string="Invoice",
        comodel_name="account.move",
        readonly=True,
        help="Invoice id that has been reconciled",
        copy=False,
        ondelete="cascade"
    )

    purchase_order_line_id = fields.Many2one(
        string="Purchase Order Line",
        comodel_name="purchase.order.line",
        readonly=True,
        help="Order line that has been reconciled (totally or partially)",
        copy=False,
        ondelete="cascade"
    )

    qty = fields.Float(
        string="Qty",
        help="Qty of product that has been reconciled",
        digits='Product Unit of Measure',
        copy=False
    )
