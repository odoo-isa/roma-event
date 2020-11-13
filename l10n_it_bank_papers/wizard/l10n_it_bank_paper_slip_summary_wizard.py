# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp


class L10nItBankPaperSlipSummaryWizard(models.TransientModel):
    _name = "l10n_it.bank_paper.slip.summary.wizard"
    _description = "Bank paper summary wizard"

    journal_id = fields.Many2one(
        string='Default Journal',
        comodel_name='account.journal',
        help="",
        copy=False
    )

    account_id = fields.Many2one(
        string='Ca. Or. Bank Account',
        comodel_name='account.account',
        help="",
        copy=False
    )

    bank_account_id = fields.Many2one(
        string='Bank Account',
        comodel_name='account.account',
        help="",
        copy=False
    )

    bank_expense_account_id = fields.Many2one(
        string='Bank Expense Account',
        comodel_name='account.account',
        help="",
        copy=False
    )

    amount = fields.Float(
        string='Amount',
        help="",
        copy=False
    )

    bank_amount = fields.Float(
        string='Bank Amount',
        help="",
        copy=False
    )

    expense_amount = fields.Float(
        string='Expense Amount',
        help="",
        copy=False
    )

    payment_type_id = fields.Many2one(
        string='Payment Type',
        comodel_name='payment.type',
        copy=False
    )

    date_maturity = fields.Date(
        string='Date Maturity',
        copy=False
    )

    partner_bank_id = fields.Many2one(
        string='Partner Bank',
        comodel_name='res.partner.bank',
        copy=True,
    )

    def _write_accreditation_line(self, bank_paper_or_bank_paper_slip_id):
        ref = "Accreditation Ri.Ba. %s" % (bank_paper_or_bank_paper_slip_id.name)
        if self.amount == 0 or self.bank_amount == 0:
            raise ValidationError(_("It's not possible to continue because amount or bank amount are 0"))
        move_id = self.env['account.move'].create({
            'ref': ref,
            'invoice_origin': ref,
            'journal_id': self.journal_id.id
        })

        balance = -self.amount
        move_line_amount_id = self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'Credit',
            'account_id': self.account_id.id,
            'move_id': move_id.id,
            'debit': balance if balance > 0 else 0.0,
            'credit': -balance if balance < 0 else 0.0,
        })

        balance = self.bank_amount
        move_line_bank_account_id = self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'Bank',
            'account_id': self.bank_account_id.id,
            'move_id': move_id.id,
            'debit': balance if balance > 0 else 0.0,
            'credit': -balance if balance < 0 else 0.0,
        })

        balance = self.expense_amount
        move_line_expense_amount_id = False
        if balance != 0.0:
            move_line_expense_amount_id = self.env['account.move.line'].with_context(check_move_validity=False).create({
                'name': 'Bank',
                'account_id': self.bank_expense_account_id.id,
                'move_id': move_id.id,
                'debit': balance if balance > 0 else 0.0,
                'credit': -balance if balance < 0 else 0.0,
            })
        bank_paper_or_bank_paper_slip_id.state = 'credited'
        bank_paper_or_bank_paper_slip_id.credit_move_id = move_id.id
        bank_paper_or_bank_paper_slip_id.bank_paper_ids.write({
            'state': 'credited'
        })
        if move_line_expense_amount_id:
            move_id.write({
                'line_ids': [
                    (6, 0, [move_line_amount_id.id, move_line_bank_account_id.id, move_line_expense_amount_id.id])]
            })
        else:
            move_id.write({
                'line_ids': [
                    (6, 0, [move_line_amount_id.id, move_line_bank_account_id.id])]
            })

    def _write_unsolved_line(self, bank_paper_or_bank_paper_slip_id):
        name = []
        ref = "Unsolved Ri.Ba. %s - line %s" % (
        bank_paper_or_bank_paper_slip_id.bank_paper_id.name, bank_paper_or_bank_paper_slip_id.seq_bank_paper)
        for line in bank_paper_or_bank_paper_slip_id.account_move_line_ids:
            if line.name:
                name.append(line.name)
            if line.date:
                name.append(line.date.strftime('%d/%m/%Y'))
        name = " - ".join(name)
        move_id = self.env['account.move'].create({
            'ref': ref,
            'invoice_origin': ref,
            'journal_id': self.journal_id.id
        })
        balance = self.amount
        move_line_amount_id = self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': name,
            'account_id': bank_paper_or_bank_paper_slip_id.partner_id.property_account_receivable_id.id,
            'partner_id': bank_paper_or_bank_paper_slip_id.partner_id.id,
            'move_id': move_id.id,
            'date_maturity': self.date_maturity,
            'debit': balance if balance > 0 else 0.0,
            'credit': -balance if balance < 0 else 0.0,
            'payment_type_id': self.payment_type_id.id,
            'res_partner_bank_id': self.partner_bank_id.id
        })
        balance = -self.bank_amount
        move_line_bank_account_id = self.env['account.move.line'].with_context(check_move_validity=False).create({
            'name': 'Bank',
            'account_id': self.bank_account_id.id,
            'move_id': move_id.id,
            'debit': balance if balance > 0 else 0.0,
            'credit': -balance if balance < 0 else 0.0,
        })
        balance = self.expense_amount
        move_line_expense_amount_id = False
        if balance != 0.0:
            move_line_expense_amount_id = self.env['account.move.line'].with_context(check_move_validity=False).create({
                'name': 'Bank',
                'account_id': self.bank_expense_account_id.id,
                'move_id': move_id.id,
                'debit': balance if balance > 0 else 0.0,
                'credit': -balance if balance < 0 else 0.0,
            })
        if move_line_expense_amount_id:
            # check if journal entry is unbalanced
            move_id.write({
                'line_ids': [
                    (6, 0, [move_line_amount_id.id, move_line_bank_account_id.id, move_line_expense_amount_id.id])]
            })
        else:
            move_id.write({
                'line_ids': [
                    (6, 0, [move_line_amount_id.id, move_line_bank_account_id.id])]
            })
        move_id.action_post()
        bank_paper_or_bank_paper_slip_id.unsolved_move_id = move_id
        for line in bank_paper_or_bank_paper_slip_id.account_move_line_ids:
            line.unsolved_move_line_id = [(6, 0, [move_line_amount_id.id])]
            invoice_ids = line.unsolved_move_line_id.get_invoice_from_move_line()
            for invoice_id in invoice_ids:
                self.env.add_to_compute(invoice_id._fields['invoice_payment_state'], invoice_id)
            bank_paper_or_bank_paper_slip_id.state = 'unpaid'

        if hasattr(line, 'accounting_entry_id'):
            move_to_join = move_id.line_ids + line
            self.env['l10n_it.accounting.entry'].join_accounting_entry(move_to_join, accounting_entry=None)

    def confirm(self):
        """
        I use the function to confirm creation of accreditation move line or unsolved move line.
        I check with context if the wizard confirm is that about accreditation or unsolved.
        I create account move and account move line
        :return:
        """
        self.ensure_one()
        bank_paper_or_bank_paper_slip_id = self.env[self._context['active_model']].browse(self._context['active_id'])
        if self._context.get('action_button') == 'accreditation':
            self._write_accreditation_line(bank_paper_or_bank_paper_slip_id)
        elif self._context.get('action_button') == 'unsolved':
            self._write_unsolved_line(bank_paper_or_bank_paper_slip_id)
