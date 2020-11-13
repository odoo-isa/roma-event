# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    counterpart_entry = fields.Many2one(
        string='Counterpart Entry',
        help=False,
        comodel_name='l10n_it.accounting.entry',
    )

    counterpart_entry_account_id = fields.Many2one(
        string='Account of the counterpart entry',
        comodel_name='account.account',
        help='''The account of the counterpart retrieved by journal if managed by accounting entry''',
        compute="_get_counterpart_entry_account_id",
        store=True
    )

    @api.depends('journal_id', 'payment_type')
    def _get_counterpart_entry_account_id(self):
        for record in self:
            record.counterpart_entry_account_id = None
            # Retrieve the default account from the journl
            if record.payment_type in ('outbound', 'transfer'):
                account_id = record.journal_id.default_debit_account_id
            else:
                account_id = record.journal_id.default_credit_account_id
            # Setting the account if it manage the accounting entry
            if account_id.managed_by_accounting_entry:
                record.counterpart_entry_account_id = account_id.id

    def _prepare_payment_moves(self):
        move_vals = super(AccountPayment, self)._prepare_payment_moves()
        # Get all the account (retrieved by the payment), that manage the accounting entry
        counterpart_entries = self.mapped('counterpart_entry_account_id').ids
        if not counterpart_entries:
            return move_vals
        for move in move_vals:
            gen = (line[2] for line in move['line_ids'] if line[2]['account_id'] in counterpart_entries)
            for line in gen:
                payment = self.browse(line['payment_id'])
                counterpart_entry = payment.counterpart_entry
                if not counterpart_entry:
                    continue
                line['accounting_entry_id'] = counterpart_entry.id
        return move_vals
