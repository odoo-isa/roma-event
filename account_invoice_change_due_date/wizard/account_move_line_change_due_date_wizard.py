# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class AccountMoveLineChangeDueDateWizard(models.TransientModel):
    _name = 'account.move.line.change.due.date.wizard'
    _description = 'Account Move Line Change Due Date Wizard'

    old_deadline_moves = fields.Many2many(
        string='Old Deadline Moves',
        help="Relation with move line of invoice, represents the current move line (not payed) of invoice",
        comodel_name='account.due.date.wizard',
        relation='old_change_due_date_wizard_rel',
        column1='chance_due_date_id',
        column2='due_date_id',
    )

    new_deadline_moves = fields.Many2many(
        string='New Deadline Moves',
        help="Relation with move line of invoice, it's possible change the value for change the due date of invoice",
        comodel_name='account.due.date.wizard',
        relation='new_change_due_date_wizard_rel',
        column1='chance_due_date_id',
        column2='due_date_id',
    )

    compute_old_amount = fields.Float(
        string='Amount',
        compute='_compute_old_amount',
        help="Compute Amount of current move line"
    )

    compute_new_amount = fields.Float(
        string='Amount',
        compute='_compute_new_amount',
        help="Compute Amount of new move line"
    )

    is_unchangeable_payment = fields.Boolean(
        string='Is Unchangeable Payment',
        help='True if payment is unchangeable (e.g. Bank papers), allows you to view an info box',
    )

    def _compute_old_amount(self):
        self.compute_old_amount = sum(x['amount'] for x in self.old_deadline_moves)

    def _compute_new_amount(self):
        self.compute_new_amount = sum(x['amount'] for x in self.new_deadline_moves)

    def _check_equal_amount(self):
        precision_rounding = self.env.company.currency_id.rounding
        if float_compare(self.compute_old_amount, self.compute_new_amount, precision_rounding=precision_rounding) != 0:
            raise ValidationError(_("It's not possible go on to the procedure, "
                                  "because the amount of old lines isn't equal to new lines"))
        return True

    def change_due_date(self):
        # Check if the amount total of current line is equal to total amount of change line
        if not self._check_equal_amount():
            return
        invoice_id = self.env['account.move'].browse(self._context.get('active_ids', False))
        filtered_line = invoice_id.line_ids.filtered(lambda l: not l.reconciled and l.date_maturity)
        if 'l10n_it.bank_paper' in self.env:
            filtered_line = filtered_line.filtered(lambda l: not l.bank_paper_id)

        if filtered_line:
            move_models = filtered_line[0]
            amount_currency = 0.0
            if move_models.currency_id:
                # Compute amount currency
                amount_currency = move_models.currency_id._convert(move_models.debit, move_models.currency_id,
                                                                   self.env.company.currency_id,
                                                                   move_models.date_maturity)

            for new_line in self.new_deadline_moves:
                # Split model line in new line and change the value
                copy_move = move_models.with_context(avoid_update_origin_line=True).\
                    split_move_line(new_line.amount, amount_currency, 'debit')
                copy_move.update({
                    'date_maturity': new_line.due_date,
                    'payment_type_id': new_line.payment_type_id,
                    'debit': new_line.amount,
                    'is_anglo_saxon_line': copy_move.is_anglo_saxon_line,
                    'is_split_line': copy_move.is_split_line
                })
            # delete old move
            for line in filtered_line:
                line.with_context(check_move_validity_for_delete=True).unlink()
        return

