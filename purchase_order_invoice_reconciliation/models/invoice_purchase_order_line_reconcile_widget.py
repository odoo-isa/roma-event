# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo.tools import float_is_zero, float_compare
from odoo import models, api
from logging import getLogger

_logger = getLogger(__name__)


class InvoicePurchaseOrderLineReconcileWidget(models.AbstractModel):
    _name = "invoice.purchase.order.line.reconcile.widget"
    _description = "Abstract class for manage 'purchase order line -> invoice' reconciliation widget"

    @api.model
    def get_invoice_view(self, invoice_id=None):
        if not invoice_id:
            return None
        invoice = self.env['account.move'].browse(invoice_id)
        html = self.env['ir.ui.view'].render_template(
            "purchase_order_invoice_reconciliation.invoice_view",
            values={
                "invoice": invoice
            }
        )
        return html

    @api.model
    def get_purchase_order_line_for_invoice_reconcile(self, invoice_id, mode='edit', **kwargs):
        # Retrieve keyword arguments
        order_ids = kwargs['order_ids'] if 'order_ids' in kwargs else []
        # Retrieve invoice
        invoice = self.env['account.move'].browse(invoice_id)
        # Retrieve already reconciled orders
        already_reconciled_order_for_invoice = invoice.mapped(
            'purchase_reconciled_line.purchase_order_line_id.order_id'
        )
        # Retrieve the orders
        order_ids = self.env['purchase.order'].browse(order_ids)
        orders = (order_ids - already_reconciled_order_for_invoice) | already_reconciled_order_for_invoice
        price_digits = self.env['decimal.precision'].precision_get('Product Price')
        values = {
            "purchase_orders": orders,
            "precision": price_digits,
            "mode": mode,
            "float_compare": float_compare,
            "float_is_zero": float_is_zero,
        }
        extra_params = self._get_extra_param(invoice, orders, kwargs)
        values.update(extra_params)
        html = self.env['ir.ui.view'].render_template(
            "purchase_order_invoice_reconciliation.order_lines",
            values=values
        )
        return html

    def _get_extra_param(self, invoice, orders, kwargs):
        return {}

    @api.model
    def get_billed_info(self, purchase_order_line=None, mode='edit'):
        order_line = self.env['purchase.order.line'].browse(purchase_order_line)
        html = self.env['ir.ui.view'].render_template(
            "purchase_order_invoice_reconciliation.reconciled_billed_info",
            values={
                "purchase_reconciliation_line": order_line.invoice_purchase_order_line_reconcile_ids,
                "mode": mode
            }
        )
        return html

    @api.model
    def reconcile_order_on_invoice(self, data, invoice_id):
        if not data or not invoice_id:
            return None
        invoice = self.env['account.move'].browse(invoice_id)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_order_reconcile = self.env['invoice.purchase.order.line.reconcile']
        for purchase_line_to_reconcile in data:
            if float_is_zero(purchase_line_to_reconcile['qty'], precision_digits=precision):
                continue
            invoice_order_reconcile += self.env['invoice.purchase.order.line.reconcile'].create({
                'invoice_id': invoice.id,
                'purchase_order_line_id': purchase_line_to_reconcile['order_line'],
                'qty': purchase_line_to_reconcile['qty'],
            })
        return {
            'reconcile_line': invoice_order_reconcile.mapped('id')
        }

    @api.model
    def unreconcile_order_on_invoice(self, reconcile_id):
        invoice_order_reconcile = self.env['invoice.purchase.order.line.reconcile'].browse(reconcile_id)
        return invoice_order_reconcile.unlink()
