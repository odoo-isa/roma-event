# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('fiscal_position_id')
    def _check_split_invoice(self):
        if self.fiscal_position_id.split_payment and self.type in ['in_invoice', 'in_refund']:
            raise ValidationError(_("It is impossible to continue, fiscal position is not consistent"))

    @api.depends('fiscal_position_id', 'fiscal_position_id.split_payment', 'invoice_line_ids')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for record in self:
            if not record.fiscal_position_id.split_payment:
                continue
            total_abs = abs(record.amount_total)
            total_currency_abs = abs(record.amount_total_signed)
            total = 0
            for line in record.line_ids.filtered(lambda l: l.tax_line_id):
                total_abs -= abs(line.price_total)
                total_currency_abs -= abs(line['amount_currency'] or line.price_total)
            if total >= 0:
                total = total_abs
                total_currency = total_currency_abs
            else:
                total = - total_abs
                total_currency = - total_currency_abs
            record.amount_residual = total
            record.amount_residual_currency = total_currency
        return res

    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        '''
        It was necessary to divide the recalculation of the accounting lines in these step: first, the lines of Split
        Payments must be eliminated; the super is then called to proceed with the standard recalculation and finally the
        registration is modified in consideration of the split payment. The unlink function was not used to remove split
        lines from posting to prevent the invalidated_cache from cleaning up the entire invoice.
        '''
        for record in self:
            record.line_ids -= self.mapped('line_ids').filtered(lambda l: l.is_split_line)
        res = super(AccountMove, self)._recompute_dynamic_lines(
                    recompute_all_taxes=recompute_all_taxes, recompute_tax_base_amount=recompute_tax_base_amount)
        for record in self:
            if not record.fiscal_position_id.split_payment:
                return res
            account_split = self.env.user.company_id.sp_account_id.id
            if not account_split:
                raise ValidationError(
                    _("Unable to validate Split Payment Invoice if Sp Account is not defined in account setting"))
            debit, credit = 0, 0
            for line in record.line_ids.filtered(lambda l: l.tax_line_id):
                if line.debit > 0 and line.credit == 0:
                    credit += line.debit
                    debit = 0
                elif line.debit == 0 and line.credit > 0:
                    credit = 0
                    debit += line.credit
                else:
                    pass
            if debit != 0 or credit != 0:
                in_draft_mode = record != record._origin
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
                    'account.move.line'].create
                candidate = create_method({
                    'name': _("Split Payment Write Off"),
                    'debit': debit,
                    'credit': credit,
                    'quantity': 1.0,
                    'move_id': self.id,
                    'date_maturity': False,
                    'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
                    'account_id': account_split,
                    'partner_id': self.commercial_partner_id.id,
                    'exclude_from_invoice_tab': True,
                    'is_split_line': True
                })
                if in_draft_mode:
                    candidate._onchange_amount_currency()
                    candidate._onchange_balance()
                record.invoice_line_ids -= candidate
        return res

    def _compute_payment_terms(self, date, total_balance, total_amount_currency):
        if self.fiscal_position_id.split_payment:
            line_ids = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in (
            'receivable', 'payable') and not line.tax_line_id)
            total_balance = sum(line_ids.mapped('balance'))
        return super(AccountMove, self)._compute_payment_terms(date, total_balance, total_balance)