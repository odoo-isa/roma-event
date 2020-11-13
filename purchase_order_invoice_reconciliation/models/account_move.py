# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_reconciled_line = fields.One2many(
        string='Purchase reconciled lines',
        comodel_name='invoice.purchase.order.line.reconcile',
        inverse_name='invoice_id',
        help="Reconciled purchase order line",
        copy=False,
    )

    total_purchase_order_reconcile_price = fields.Monetary(
        string='Total price reconcile form purchase order (Untaxed)',
        digits='Product Price',
        help="Total reconciled from purchase orders",
        compute="_compute_total_reconcile_from_purchase_order"
    )

    invoice_check_status = fields.Selection(
        string='Invoice check status',
        default='open',
        selection=[
            ('open', 'Open'),
            ('close', 'Closed'),
            ('close_unbalance', 'Close with unbalance invoice and orders'),
            ('close_unbalance_invoice', 'Closed with unbalance invoice'),
            ('close_unbalance_orders', 'Closed with unbalance orders')
        ],
        help="""This field indicate the status of the invoice check""",
        copy=False,
    )

    def _compute_total_reconcile_from_purchase_order(self):
        """
        This function compute the total amount of purchase order line reconciliation
        :return: The total of reconciliation amount (float)
        """
        for invoice in self:
            reconciled_lines = self.env['invoice.purchase.order.line.reconcile'].search([
                ('invoice_id', '=', invoice.id)
            ])
            invoice.total_purchase_order_reconcile_price = sum([
                x.qty * x.purchase_order_line_id.price_unit for x in reconciled_lines
            ])

    def invoice_purchase_order_line_reconcile(self):
        """
        This function open the view of reconciliation widget
        :return: the reconciliation widget view
        """
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "invoice_purchase_order_line_reconcile",
            "name": "Order line invoice reconciliation",
            "params": {
                "invoice_id": self.id,
                "supplier_id": self.partner_id.id,
                "mode": self.env.context['mode'] if 'mode' in self.env.context else 'edit'
            }
        }

    def open_reconcile_order(self):
        """
        This function open the purchase order linked to this invoice
        :return: the purchase order view
        """
        self.ensure_one()
        order_id = self.mapped('purchase_reconciled_line.purchase_order_line_id.order_id.id')
        return {
            "name": "Purchase order(s)",
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [
                ['id', 'in', order_id]
            ],
        }

    def invoice_end_purchase_check(self):
        """
        This function close the check for the supplier invoice respect the purchase orders.
        Performs some checks:
        Invoice check:
         - If unbalance between amount untaxed of the invoice and the amount of reconciliation ask to the user the
           reason
        Order check:
         - Retrieve all the purchase orders linked to this invoice
         - For each of these order check if the amount reconciled is unbalance respect the amount of the order
            * If unbalance ask to the user the reason (the same for the invoice.)
        There are three buttons:
         - Cancel -> Cancel the current operation.
         - Close the invoice but not orders -> Set the invoice as checked but the order have to be close manually
         - Close the invoice and the orders -> Set the invoice as checked and the order as fully invoiced. Set the
           reason for the unbalance orders if the user provided it.
        :return: view for widget reason if there is unbalance otherwise void
        """
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Product Price')
        # Prepare context
        context = dict()
        # Check for invoice reconcile unbalance
        invoice_unbalance = float_compare(
            self.amount_untaxed,
            self.total_purchase_order_reconcile_price,
            precision_digits=precision
        )
        if invoice_unbalance != 0:
            context['invoice_unbalance'] = True
        # Check the order that is unbalance
        unbalance_order = list()
        orders = self.purchase_reconciled_line.mapped('purchase_order_line_id.order_id')
        for order in orders:
            if float_compare(order.billed_amount_untaxed, order.amount_untaxed, precision_digits=precision)!=0:
                unbalance_order.append(order)
        # If there aren't unbalance neither with invoice neither with the orders, close the invoice and all orders
        if not invoice_unbalance and not unbalance_order:
            self.set_invoice_check_status('close')
            orders.set_as_invoiced()
            return True
        # Otherwise show reason wizard
        else:
            values = dict()
            if invoice_unbalance:
                values['invoice'] = self
            if unbalance_order:
                values['orders'] = unbalance_order
                context['unbalance_orders'] = [x.id for x in unbalance_order]
            html = self.env['ir.ui.view'].render_template(
                "purchase_order_invoice_reconciliation.invoice_close_check",
                values=values
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
                "context": context
            }

    def set_invoice_check_status(self, value):
        """
        Set the state of the invoice status check
        :param value: filed's selection value
        :return: void
        """
        for record in self:
            record.invoice_check_status = value

    def invoice_reopen_purchase_check(self):
        for move in self:
            # Reopen all the linked order's
            move.purchase_reconciled_line.mapped('purchase_order_line_id.order_id').button_reopen_invoice_state()
            # Reopen the invoice check status
            move.invoice_check_status = 'open'
            move.message_post(
                body=_(
                    "The invoice reconcile's check it was reopen."
                )
            )

    def button_draft(self):
        """
        Inherit method for check if exist reconcile movements before to set invoice as draft
        :return: raise UserError if reconcile movements are present
        """
        for move in self:
            if any(move.purchase_reconciled_line):
                raise UserError(_(
                    "Unable to set invoice in draft state: there are reconcile movements that have to be cancel."
                ))
        return super(AccountMove, self).button_draft()

    def action_invoice_register_payment(self):
        """
        Inherit method: If invoice is not declare as check with the purchase order it is not possible register payment.
        :return: raise UserError if invoice check status is open
        """
        for move in self:
            if move.type.startswith('out_'):
                continue
            if move.invoice_check_status == 'open':
                raise UserError(_(
                    "Unable to register payment for invoice that have to be yet check"
                ))
        return super(AccountMove, self).action_invoice_register_payment()
