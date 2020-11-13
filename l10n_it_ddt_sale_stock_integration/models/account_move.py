# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import float_is_zero, float_compare
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_delivery_expense(self, precision):
        """
        Create or update delivery expense invoice line
        Update if:
            - Exists same delivery product with same price unit
        :param invoice: the invoice (account move)
        :param precision: decimal invoice precision
        :return: void
        """
        res = super(AccountMove, self)._compute_delivery_expense(precision=precision)
        for record in self:
            delivery_lines = record.mapped('invoice_line_ids.sale_line_ids.order_id.order_line').filtered(lambda l:
                l.is_delivery and not float_is_zero(l.qty_to_invoice, precision_digits=precision)
            )
            for delivery_line in delivery_lines:
                delivery_invoice = record.invoice_line_ids.filtered(lambda l:
                    l.product_id == delivery_line.product_id and
                    float_compare(delivery_line.price_unit, l.price_unit, precision_digits=precision) == 0
                )
                if delivery_invoice:
                    delivery_invoice.quantity += delivery_line.product_uom_qty
                else:
                    # Force prepare the invoice line for delivery expense
                    invoice_vals = delivery_line._prepare_invoice_line()

                    # Retrieving account to add to the account move line for the expense, first on product then to the
                    # category linked to the product.
                    account_id = None
                    if delivery_line.product_id.product_tmpl_id.property_account_income_id:
                        account_id = delivery_line.product_id.product_tmpl_id.property_account_income_id.id
                    elif delivery_line.product_id.product_tmpl_id.categ_id and delivery_line.product_id.product_tmpl_id.categ_id.property_account_income_categ_id:
                        account_id = delivery_line.product_id.product_tmpl_id.categ_id.property_account_income_categ_id.id
                    invoice_vals.update(move_id=record.id,
                                        account_id=account_id)

                    # Create the move line and then check balancing on invoice.
                    self.env['account.move.line'].with_context(check_move_validity=False).create(invoice_vals)
                    record.with_context(check_move_validity=False)._recompute_dynamic_lines(
                        recompute_all_taxes=True,
                        recompute_tax_base_amount=True)
                    record._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
        return res
