# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.tools import date_utils
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError
import queue


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_unsolved_widget = fields.Html(
        compute="_compute_unsolved_widget_info"
    )

    def _compute_unsolved_widget_info(self):
        for move in self:
            if move.state != 'posted' or not move.is_invoice(include_receipts=True):
                move.invoice_unsolved_widget = False
                continue
            unsolved_vals = self._get_unsolved_vals(move)
            if unsolved_vals:
                move.invoice_unsolved_widget = self.env['ir.ui.view'].render_template(
                    "l10n_it_bank_papers.unsolved_template", values=dict(lines=unsolved_vals))
            else:
                move.invoice_unsolved_widget = ""

    def _get_unsolved_vals(self, move):
        all_move = self._get_all_move_invoices(move)
        if all_move:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            all_move = all_move.filtered(
                lambda l: float_compare(l.amount_residual, 0.0, precision_digits=precision)
                and l.unsolved_move_of
            )

        return all_move

    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for move in self:
            if move.is_invoice(include_receipts=True):
                move._get_payment_info()
        return res

    def _get_payment_info(self):
        self.ensure_one()
        total_residual = self.amount_residual
        in_payment_set = {}
        currencies = set()
        lines = self._get_all_move_invoices(self)
        lines = lines - self.line_ids
        if not lines:
            return
        for line in lines:
            if line.currency_id:
                currencies.add(line.currency_id)
            # Residual amount.
            total_residual += line.amount_residual_currency if len(currencies) == 1 else line.amount_residual
        if self.type == 'entry' or self.is_outbound():
            sign = 1
        else:
            sign = -1
        self.amount_residual = -sign * total_residual
        self.amount_residual_signed = total_residual

        currency = len(currencies) == 1 and currencies.pop() or self.company_id.currency_id
        is_paid = currency and currency.is_zero(self.amount_residual) or not self.amount_residual

        # Compute 'invoice_payment_state'.
        if self.type == 'entry':
            self.invoice_payment_state = False
        elif self.state == 'posted' and is_paid:
            if self.id in in_payment_set:
                self.invoice_payment_state = 'in_payment'
            else:
                self.invoice_payment_state = 'paid'
        else:
            self.invoice_payment_state = 'not_paid'

    def _get_all_move_invoices(self, move):
        # This function return all move line of passed invoices and all unsolved line
        Q = queue.Queue()
        lines_res = self.env['account.move.line']
        line_ids = move.mapped('line_ids')
        for line in line_ids:
            Q.put(line)
        while not Q.empty():
            move_line = Q.get()
            lines_res += move_line
            if move_line.unsolved_move_line_id:
                Q.put(move_line.unsolved_move_line_id)
        lines_res = lines_res.filtered(lambda l: l.account_id == l.partner_id.property_account_receivable_id)
        # Delete duplicate with Union (simbol |),
        line_res_without_duplicate = lines_res | lines_res
        return line_res_without_duplicate

    def unlink(self):
        invoice_to_recompute = self.env['account.move']
        # Save the invoice that should be recompute the state because unsolved move has been removed.
        for record in self:
            bank_paper_id = record.env['l10n_it.bank_paper'].search([('unsolved_move_id', '=', record.id)])
            if bank_paper_id:
                bank_paper_id.state = 'credited'
                for line in bank_paper_id.account_move_line_ids:
                    invoice_ids = line.unsolved_move_line_id.get_invoice_from_move_line()
                    for invoice_id in invoice_ids:
                        invoice_to_recompute += invoice_id
        res = super(AccountMove, self.with_context(force_delete=True)).unlink()
        for invoice_id in invoice_to_recompute:
            self.env.add_to_compute(invoice_id._fields['invoice_payment_state'], invoice_id)
        return res

    def button_draft(self):
        """
        Inherit method for check if exist Bank Paper movements, if there are return UserError
        :return: raise UserError if Bank Paper movements are present
        """
        for move in self:
            bank_papers = self.env['l10n_it.bank_paper'].search([("account_move_line_ids", "in", move.line_ids.mapped("id"))])
            if bank_papers:
                raise UserError(_("It isn't possible to draft the invoice. "
                                  "There are one or more Bank papers linked to the move line."))
        return super(AccountMove, self).button_draft()
