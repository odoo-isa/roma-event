# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class L10nItDdtLine(models.Model):
    _inherit = 'l10n_it.ddt.line'

    sale_order_line_id = fields.Many2one(
        string='Sale order line',
        comodel_name='sale.order.line',
        ondelete="restrict",
        help="Link this ddt line to sale order line",
        copy=False,
    )


    discount = fields.Float(
        string='Discount (%)',
        digits='Discount',
        default=0.0
    )

    def _prepare_invoice_line(self, qty, num_line=0):
        self.ensure_one()
        res = super(L10nItDdtLine, self)._prepare_invoice_line(qty)
        res['sale_line_ids'] = [(6, 0, self.sale_order_line_id.ids)]
        res['discount'] = self.sale_order_line_id.discount
        if self.sale_order_line_id.order_id.analytic_account_id:
            res['analytic_account_id'] = self.sale_order_line_id.order_id.analytic_account_id.id
        return res
