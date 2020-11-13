# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, _
from logging import getLogger

_logger = getLogger(__name__)


class UnbalanceReconciliationReasonWizard(models.TransientModel):
    _name = 'unbalance.reconciliation.reason.wizard'
    _description = 'Wizard for message reconciliation confirm'

    message_info = fields.Html(
        string='Message info',
        readonly=True,
    )

    reason = fields.Char(
        string='Reason',
        help="Short annotation that indicate the motivation of the reconciliation.",
    )

    def confirm_invoice_check(self):
        self.ensure_one()
        invoice = self.env['account.move'].browse(self.env.context['active_id'])
        invoice_unbalance = False
        unbalance_orders = []
        if 'invoice_unbalance' in self.env.context:
            invoice_unbalance = self.env.context['invoice_unbalance']
        if 'unbalance_orders' in self.env.context:
            unbalance_orders = self.env.context['unbalance_orders']
        # Close the invoice. If there is unbalance log reason.
        if invoice_unbalance:
            if unbalance_orders:
                invoice.set_invoice_check_status('close_unbalance')
            else:
                invoice.set_invoice_check_status('close_unbalance_invoice')
        else:
            # If there isn't unbalance with invoice there is only with order (otherwise we can't arrive at this point
            # because the closing with not unbalance is manage directly in the invoice object).
            invoice.set_invoice_check_status('close_unbalance_orders')
        # Close the order's. The unbalance with log the other without it.
        orders = invoice.purchase_reconciled_line.mapped('purchase_order_line_id.order_id')
        # Only the order that is not already closed
        orders = orders.filtered(lambda o: o.invoice_status == 'to invoice')
        for order in orders:
            if order.id in unbalance_orders:
                order.message_post(
                    body=_("%s<br/>Reason: %s" % (
                        self.message_info,
                        self.reason
                    ))
                )
            order.set_as_invoiced()
        # Log the invoice message
        invoice.message_post(
            body=_("%s<br/><span class='font-weight-bold'>Reason:</span> %s" % (
                self.message_info,
                "<span style='font-size: 14px'>%s</span>" % self.reason or _("No reason specified")
            ))
        )

    def confirm_reconcile_order(self):
        self.ensure_one()
        order = self.env['purchase.order'].browse(self.env.context['active_id'])
        order.message_post(
            body=_("%s<br/><span class='font-weight-bold'>Reason:</span> %s" % (
                self.message_info,
                "<span style='font-size: 14px'>%s</span>" % self.reason or _("No reason specified")
            ))
        )
        order.set_as_invoiced()
