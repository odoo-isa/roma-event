# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
import queue
_logger = getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bank_paper_id = fields.Many2one(
        string='Bank Paper',
        comodel_name='l10n_it.bank_paper',
        help="",
        copy=False
    )

    bank_paper_slip_id = fields.Many2one(
        string='Bank Paper Slip',
        comodel_name='l10n_it.bank_paper.slip',
        help="",
        copy=False
    )

    unsolved_move_line_id = fields.Many2many(
        string='Unsolved Move Line',
        help="",
        comodel_name='account.move.line',
        relation='account_move_line_account_move_line_rel',
        column1='account_move_line_id',
        column2='unsolved_move_line_id',
        copy=False,
    )

    unsolved_move_of = fields.Many2many(
        string='Unsolved Move of',
        help="Inverse of Unsolved Move Line ",
        comodel_name='account.move.line',
        relation='account_move_line_account_move_line_rel',
        column1='unsolved_move_line_id',
        column2='account_move_line_id',
        copy=False,
    )

    is_bank_paper_line = fields.Boolean(
        string='bank Paper Line',
        help='This flag indicates that this line is part of a Bank Paper',
        copy=False,
    )

    def get_account_move_line_for_riba(self, payment_type_id):
        move_line = self.search([
            ('move_id.type', 'in', ['out_invoice', 'out_refund']),
            ('move_id.state', 'not in', ['draft', 'paid', 'cancel']),
            ('full_reconcile_id', 'in', [None, False]),
            ('move_id.journal_id.type', '!=', 'purchase'),
            ('account_id.related_account_type', '=', 'receivable'),
            ('bank_paper_id', 'in', [None, False]),
            ('payment_type_id', '=', payment_type_id.id)
        ])
        move_line_not_invoice = self.search([
            ('full_reconcile_id', 'in', [None, False]),
            ('account_id.related_account_type', '=', 'receivable'),
            ('bank_paper_id', 'in', [None, False]),
            ('payment_type_id', '=', payment_type_id.id)
        ])
        for line in move_line_not_invoice:
            try:
                invoice_ids = line.get_invoice_from_move_line()
                if not invoice_ids:
                    continue
                for invoice_id in invoice_ids:
                    if invoice_id.type not in ['out_invoice', 'out_refund']:
                        continue
                    if invoice_id.state in ['draft', 'paid', 'cancel']:
                        continue
                    if invoice_id.journal_id.type == 'purchase':
                        continue
                move_line += line
            except ValidationError:
                if not line.reconciled:
                    move_line += line
        return move_line

    def _check_iban(self, iban):
        """
        Check if all iban in iban list are the same
        :param iban:
        :return: iban
        """
        if all(x == iban[0] for x in iban):
            return iban[0]
        else:
            raise ValidationError(_("Res Partner Bank of account move lines don't match"))

    def remove_move_reconcile(self):
        move_lines = self.env['account.move.line']
        move_lines += self
        move_lines += self.mapped('matched_credit_ids.credit_move_id')
        move_lines += self.mapped('matched_debit_ids.debit_move_id')
        if any([x.bank_paper_id for x in move_lines]):
            raise ValidationError(_("It's not possible to remove move reconcile because some of them is linked to bank paper"))
        return super(AccountMoveLine, self).remove_move_reconcile()

    def get_invoice_from_move_line(self):
        all_move_lines = self.env['account.move.line']
        Q = queue.Queue()
        for m in self:
            Q.put(m)
        while not Q.empty():
            move_line = Q.get()
            all_move_lines += move_line
            # Considero l'insoluto
            unsolved_move_line_ids = self.search([('unsolved_move_line_id', 'in', move_line.id)])
            if unsolved_move_line_ids:
                for m in unsolved_move_line_ids:
                    Q.put(m)
            # Considero le riconciliazioni
            account_partial_reconcile = self.env['account.partial.reconcile']
            account_partial_reconcile += move_line.matched_debit_ids
            account_partial_reconcile += move_line.matched_credit_ids
            lines = account_partial_reconcile.mapped('debit_move_id')
            lines += account_partial_reconcile.mapped('credit_move_id')
            lines -= move_line
            lines -= all_move_lines
            if lines:
                for m in lines:
                    Q.put(m)
        invoice_ids = all_move_lines.mapped('move_id').filtered(lambda move:move.is_invoice(include_receipts=True))
        return invoice_ids

    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        """
        This function force the recompute for the state of the account invoice if unsolved moves are present
        """
        # Search the invoice from moves to reconcile before the super because if l10n_it_account_balances module is
        # installed could change the self.
        all_move = self
        invoice_ids = None
        # When reconcile a payment (from wizard payment in invoice), invoked all move line(also unsolved)
        # and recompute the amount
        if self.mapped('payment_id'):
            payment_id = self.filtered(lambda l:l.payment_id).payment_id
            invoice_ids = payment_id.invoice_ids
            all_move = self.env['account.move']._get_all_move_invoices(invoice_ids)
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            all_move = all_move | self
            all_move = all_move.filtered(lambda l: float_compare(l.amount_residual, 0.0, precision_digits=precision))
        if self.search([('unsolved_move_line_id', 'in', self.ids)]):
            invoice_ids = self.get_invoice_from_move_line()
        res = super(AccountMoveLine, all_move).reconcile(writeoff_acc_id, writeoff_journal_id)
        if invoice_ids:
            for invoice_id in invoice_ids:
                self.env.add_to_compute(invoice_id._fields['invoice_payment_state'], invoice_id)
        return res

    def remove_move_reconcile(self):
        """
        This function force the recompute for the state of the account invoice if unsolved moves are present
        """
        # Get all impacted moves
        moves = []
        moves += self.ids
        moves += self.mapped('matched_credit_ids.credit_move_id.id')
        moves += self.mapped('matched_debit_ids.debit_move_id.id')
        moves = list(set(moves))
        moves = self.env['account.move.line'].browse(moves)
        # Search the invoice from moves to reconcile before the super because if l10n_it_account_balances module is
        # installed could change the self.
        invoice_ids = []
        if self.search([('unsolved_move_line_id', 'in', moves.ids)]):
            invoice_ids = moves.get_invoice_from_move_line()
        res = super(AccountMoveLine, self).remove_move_reconcile()
        for invoice_id in invoice_ids:
            if invoice_id:
                self.env.add_to_compute(invoice_id._fields['invoice_payment_state'], invoice_id)
        return res
