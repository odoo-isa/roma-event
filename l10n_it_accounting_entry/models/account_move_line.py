# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from collections import defaultdict
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    accounting_entry_id = fields.Many2one(
        string='Accounting entry',
        index=True,
        comodel_name='l10n_it.accounting.entry',
        ondelete="set null",
        help='This is the accounting entry. Will be generated automatically at the post action '
             'or it can be set manually',
        copy=False,
    )

    has_accounting_entry_management = fields.Boolean(
        string='Has accounting entry management',
        help='System field that indicate if account line haa the management of the accounting entry',
        related='account_id.managed_by_accounting_entry',
        readonly=True
    )

    def write(self, vals):
        """
        If change the value for accounting_entry_id have to ensure that the entry does not remain orphan.
        So call explicit the check for orphan entry
        :param vals:
        :return:
        """
        prev_entries = None
        if 'accounting_entry_id' in vals:
            # Retrieve the previous accounting entry
            prev_entries = self._origin.accounting_entry_id
        res = super(AccountMoveLine, self).write(vals)
        if prev_entries:
            prev_entries.remove_orphan_accounting_entries()
        return res

    def remove_move_reconcile(self):
        """ Undo a entry statement automatic join (during reconciliation) """
        moves_line = self.mapped('matched_debit_ids.credit_move_id')
        moves_line += self.mapped('matched_debit_ids.debit_move_id')
        moves_line += self.mapped('matched_credit_ids.credit_move_id')
        moves_line += self.mapped('matched_credit_ids.debit_move_id')
        if moves_line:
            self.env['l10n_it.accounting.entry'].split_accounting_entry(moves_line)
        return super(AccountMoveLine, self).remove_move_reconcile()

    def shall_assign_accounting_entry(self):
        """
        This function generate and assign the accounting entry for the move lines. Will be generated one accounting
        entry for each grouped key tuple (default to move_id, account_id)
        :return: True
        """
        # We must generate accounting entry for the lines for which it isn't set.
        lines_to_generate_entries = self.filtered(
            lambda l: l.has_accounting_entry_management and not l.accounting_entry_id
        )
        grouped_lines = defaultdict(self.env['account.move.line'].browse)
        for line in lines_to_generate_entries:
            key = line._get_grouped_accounting_key()
            grouped_lines[key] += line
        # For each group create the accounting entry
        generated_entries = self.env['l10n_it.accounting.entry']
        for key, lines in grouped_lines.items():
            generated_entries += self.env['l10n_it.accounting.entry'].generate_accounting_entry(key, lines)
        return generated_entries

    def _get_grouped_accounting_key(self):
        """
        Return the tuple key for grouping account move lines for impute the accounting entry
        :return: the grouping value tuple
        """
        return self.move_id, self.partner_id, self.account_id

    def _get_default_value(self, debit_credit, amount, amount_currency) -> dict:
        """
        We have to inherit the default data for copy on split for adding accounting entry value.
        """
        res = super(AccountMoveLine, self)._get_default_value(debit_credit, amount, amount_currency)
        res.update({
            'accounting_entry_id': self.accounting_entry_id.id
        })
        return res
