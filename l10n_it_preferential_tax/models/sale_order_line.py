# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if not self.product_id:
            return res

        preferential_taxes = self.order_id.partner_shipping_id.mapped('account_preferential_taxes_ids').filtered(
            lambda v: v.active_tax and v.released_date <= self.order_id.date_order.date() <= v.expiration_date
        )
        if self.product_id.preferential_tax_na or self.product_id.categ_id.preferential_tax_na:
            return res

        tax = None
        for tax_id in self.product_id.taxes_id:
            if not tax:
                tax = tax_id
                continue
            if tax_id.amount < tax.amount:
                tax = tax_id

        for preferential_tax in preferential_taxes:
            if not tax:
                tax = preferential_tax.preferential_tax_id.tax_id
                continue

            if preferential_tax.preferential_tax_id.tax_id.amount < tax.amount:
                tax = preferential_tax.preferential_tax_id.tax_id

        if tax:
            self.tax_id = [(6, 0, [tax.id])]
        return res
