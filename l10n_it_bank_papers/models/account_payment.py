# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date):
        # When the payment wizard is called, the amount field is recalculated.
        # In the case of unsolved payments, the calculation is incorrect because not all lines are considered
        # With this function all move, (unsolved include) are calculated
        total = super(AccountPayment, self)._compute_payment_amount(invoices, currency, journal, date)
        lines = invoices.mapped('line_ids').filtered(lambda l: l.account_id == l.partner_id.property_account_receivable_id)
        all_move_line = self.env['account.move']._get_all_move_invoices(invoices)
        all_move_line = all_move_line - lines
        company = journal.company_id
        for line in all_move_line:
            if line.move_id.currency_id == currency and currency != company.currency_id:
                total += line.amount_residual_currency
            else:
                total += company.currency_id._convert(line.amount_residual, currency, company, date)
        return total
