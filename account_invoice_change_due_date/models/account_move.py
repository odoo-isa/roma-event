# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _create_wizard_deadlines(self, move_lines, is_unchangeable_payment):
        """
        :param move: filtered move lines, useful to create line of wizard
        :return: result to display on wizard
        """
        if not move_lines:
            return False
        change_line = self.env['account.move.line.change.due.date.wizard'].create(
            {'is_unchangeable_payment': is_unchangeable_payment}
        )
        for line in move_lines:
            object_old_line = self.env['account.due.date.wizard'].create(
                {'due_date': line.date_maturity,
                 'payment_type_id': line.payment_type_id.id,
                 'amount': line.debit,
                 })
            object_new_line = object_old_line.copy()
            change_line.old_deadline_moves = [(4, object_old_line.id, False)]
            change_line.new_deadline_moves = [(4, object_new_line.id, False)]
        res_id = change_line.id if change_line else False
        return res_id

    def get_move_lines_to_change(self):
        """
        :return: View for change due date with filtered move
        """
        self.ensure_one()
        # Filter move for not payed and date matuity
        filter_move_line = self.line_ids.filtered(lambda l: not l.reconciled and l.date_maturity)
        is_unchangeable_payment = False
        # If bank paper module is installed
        if 'l10n_it.bank_paper' in self.env:
            bank_paper_line = filter_move_line.filtered(lambda l: l.bank_paper_id)
            if bank_paper_line:
                filter_move_line = filter_move_line - bank_paper_line
                is_unchangeable_payment = True
        res_id = self._create_wizard_deadlines(filter_move_line, is_unchangeable_payment)

        return {
            'name': 'Change Due Date',
            'view_mode': 'form',
            'target': 'new',
            'res_id': res_id,
            'res_model': 'account.move.line.change.due.date.wizard',
            'type': 'ir.actions.act_window',
        }

