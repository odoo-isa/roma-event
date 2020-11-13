# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    billed_amount_untaxed = fields.Float(
        string='Billed amount untaxed',
        digits='Product Price',
        help='''The reconciled amount between this purchase order and invoice(s)''',
        compute="_compute_billed_amount_untaxed",
        store=True
    )

    forced_as_billed = fields.Boolean(
        string='Forced as billed',
        help="This order it was forced as billed",
        default=False
    )

    internal_reference = fields.Char(
        string='Internal reference',
        help="""Mnemonic reference to the purchase order""",
        copy=False,
    )

    @api.depends('order_line.invoice_purchase_order_line_reconcile_ids')
    def _compute_billed_amount_untaxed(self):
        for order in self:
            order.billed_amount_untaxed = sum([
                x.qty * x.purchase_order_line_id.price_unit
                for x in order.mapped('order_line.invoice_purchase_order_line_reconcile_ids')
            ])

    @api.depends('order_line.invoice_purchase_order_line_reconcile_ids')
    def _compute_invoice(self):
        res = super(PurchaseOrder, self)._compute_invoice()
        for order in self:
            invoices = order.mapped('order_line.invoice_purchase_order_line_reconcile_ids.invoice_id')
            order.invoice_ids = order.invoice_ids | invoices
            order.invoice_count = len(order.invoice_ids)
        return res

    def button_close_reconcile(self):
        # Only one order at time (there is check a check for the amount)
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Product Price')
        compare = float_compare(self.billed_amount_untaxed, self.amount_untaxed, precision_digits=precision)
        if compare != 0:
            html = self.env['ir.ui.view'].render_template(
                "purchase_order_invoice_reconciliation.order_set_billed",
                values={
                    'order': self
                }
            )
            wizard_id = self.env['unbalance.reconciliation.reason.wizard'].create({
                'message_info': html
            })
            return {
                "type": "ir.actions.act_window",
                "res_model": "unbalance.reconciliation.reason.wizard",
                "views": [[False, "form"]],
                "res_id": wizard_id.id,
                "target": "new",
            }
        else:
            self.message_post(
                body=_(
                    "The order it was set as invoiced."
                )
            )
            self.set_as_invoiced()

    def set_as_invoiced(self):
        for record in self:
            record.forced_as_billed = True
            record.invoice_status = 'invoiced'

    def _get_invoiced(self):
        super(PurchaseOrder, self)._get_invoiced()
        for order in self:
            if order.forced_as_billed:
                order.invoice_status = 'invoiced'

    def button_reopen_invoice_state(self):
        for order in self:
            order.ensure_one()
            order.forced_as_billed = False
            order.invoice_status = 'to invoice'
            order.message_post(
                body=_(
                    "The invoice status's order it was set as to invoice."
                )
            )
