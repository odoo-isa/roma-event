# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class InvoicePurchaseOrderLineReconcileWidget(models.AbstractModel):
    _inherit = "invoice.purchase.order.line.reconcile.widget"

    def _get_extra_param(self, invoice, orders, kwargs):
        params = super(InvoicePurchaseOrderLineReconcileWidget, self)._get_extra_param(invoice, orders, kwargs)
        orders_from_ddt = {}
        ddt_ids = kwargs['ddt_ids']
        ddt_ids = ddt_ids.split(';')
        pickings = self.env['stock.picking'].search([
            ('ddt_in', 'in', ddt_ids),
            ('partner_id', '=', invoice.partner_id.id)
        ])
        purchase_line_id = pickings.mapped('move_lines.purchase_line_id')
        # Select only purchase order line that there isn't already loaded
        purchase_line_id = purchase_line_id.filtered(lambda l: l.order_id not in orders)
        # Prepare data structure
        orders = purchase_line_id.mapped('order_id')
        for order in orders:
            orders_from_ddt[order] = purchase_line_id.filtered(lambda l: l.order_id == order)
        params['order_from_ddt'] = orders_from_ddt
        return params
