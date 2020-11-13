# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import RedirectWarning, ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    def _create_tax_basis_move(self):
        """
        This function is inherit in order to set the correct data in the account move for the withholding tax
        :return:
        """
        moves = super(AccountPartialReconcile, self)._create_tax_basis_move()
        if not self._is_withholding_tax_exigibility():
            return moves
        # if withholding tax retrieve the journal and the payment term that should be set
        withholding_journal = self.company_id.withholding_journal_id
        payment_term = self.company_id.withholding_payment_term
        if not all([withholding_journal, payment_term]):
            action = self.env.ref('account.action_account_config')
            msg = _(
                'Cannot find parameter for the withholding tax, You should configure it. '
                '\nPlease go to Account Configuration.')
            raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
        # The date will be set in _set_tax_cash_basis_entry_date function
        moves.write({
            'journal_id': withholding_journal.id,
            'is_withholding_tax': True
        })
        return moves

    def _set_tax_cash_basis_entry_date(self, move_date, newly_created_move):
        """
        This function is inherit in order to set the correct data in the account move for the withholding tax
        :return:
        """
        res = super(AccountPartialReconcile, self)._set_tax_cash_basis_entry_date(move_date, newly_created_move)
        # check if withholding tax
        if not self._is_withholding_tax_exigibility():
            return res
        # Retrieve the payment term from the configuration
        payment_term_wth = self.company_id.withholding_payment_term
        # I want only know the expired date so pass a fake amount
        rate = payment_term_wth.compute(100, date_ref=newly_created_move.date)
        if not rate:
            return res
        rate = rate[0]
        values = {
            'date_maturity': rate[0]
        }
        if hasattr(self.env['account.move.line'], 'payment_type_id'):
            values.update({
                'payment_type_id': rate[2].get('payment_type_id')
            })
        newly_created_move.line_ids.write(values)
        return res

    def _is_withholding_tax_exigibility(self):
        """
        Check if move is tax exigibility for withholding tax
        :return:
        """
        taxes_type = (self.debit_move_id.move_id + self.credit_move_id.move_id).line_ids.mapped('tax_ids').filtered(
            lambda t: t.tax_exigibility == 'on_payment'
        ).mapped('account_tax_type')
        return all([x == 'withholding_tax' for x in taxes_type])

    def unlink(self):
        """
        Cannot remove reconcile of withholding moves that it was payment
        :return:
        """
        # Search for linked deferred move lines
        moves = self.env['account.move'].search([('tax_cash_basis_rec_id', 'in', self._ids)])
        # Search for reconcile lines
        moves_line_withholding_payment = (
                moves.mapped('line_ids') + self.credit_move_id + self.debit_move_id
        ).mapped('l10n_it_payment_withholding_tax_id')
        if moves_line_withholding_payment and 'avoid_withholding_pay_check' not in self.env.context:
            move_withholding_payment = moves_line_withholding_payment.mapped('move_id')
            raise ValidationError(_(
                f"Cannot reverse a withholding move that it was payment: "
                f"{', '.join(move_withholding_payment.mapped('name'))}. Please cancel these withholding payment."
            ))
        super(AccountPartialReconcile, self).unlink()
