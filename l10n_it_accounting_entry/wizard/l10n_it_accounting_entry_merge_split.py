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


class L10nItAccountingEntryMergeSplit(models.TransientModel):
    _name = 'l10n_it.accounting.entry.merge.split'
    _description = 'Merge or Split multiple accounting entries'

    main_accounting_entry = fields.Many2one(
        string='Main accounting entry',
        comodel_name='l10n_it.accounting.entry',
        help='All the moves will be linked to this accounting entry.',
    )

    accounting_entry_to_split = fields.Many2many(
        string='Accounting entry to split',
        comodel_name='l10n_it.accounting.entry',
        relation='l10n_it_accounting_entry_split_rel_wizard',
        help="If operation is split must be specified the accounting entry to split"
    )

    @api.model
    def default_get(self, fields_list):
        """
        Perform some check
        :param fields_list:
        :return:
        """
        active_ids = self._context['active_ids']
        action = self._context['action']
        if action == 'merge':
            self._default_get_merge()
        elif action == 'split':
            if len(active_ids) < 1:
                raise ValidationError(_(
                    "Select at least one account entry to split"
                ))
        else:
            raise ValidationError("Unrecognized action (split/merge)")
        return super(L10nItAccountingEntryMergeSplit, self).default_get(fields_list)

    def _default_get_merge(self):
        active_model = self._context['active_model']
        active_ids = self._context['active_ids']
        if active_model == 'l10n_it.accounting.entry':
            entry = self.env['l10n_it.accounting.entry'].browse(active_ids)
            move_lines = entry.accounting_entry_lines
        elif active_model == 'account.move':
            moves = self.env['account.move'].browse(active_ids)
            entry = moves.mapped('accounting_entry_ids')
            move_lines = moves.mapped('line_ids')
        elif active_model == 'account.move.line':
            move_lines = self.env['account.move.line'].browse(active_ids)
            entry = move_lines.mapped('accounting_entry_id')
        else:
            raise ValidationError(_(
                "This operation cannot be performed from this model %s." % active_model
            ))
        if len(entry) <= 1:
            raise ValidationError(_(
                "Select at least two accounting entry to merge."
            ))
        # Only entry with same account/partner
        if len(move_lines.mapped('partner_id.id')) > 1:
            raise ValidationError(_(
                "Unable to merge accounting entries with different partner"
            ))
        if len(move_lines.mapped('account_id.id')) > 1:
            raise ValidationError(_(
                "Unable to merge accounting entries with different account"
            ))
        # Only with same company
        if len(set([entry.company_id for entry in entry])) > 1:
            raise ValidationError(_(
                "Unable to merge accounting entries from different company"
            ))

    @api.onchange('accounting_entry_to_split')
    def set_domain_for_entry_to_split(self):
        action = self._context['action']
        domain_ids = self._retrieve_domain_for_split_merge()
        if action == 'split':
            if len(domain_ids) == 1 or self._context['active_model'] == 'l10n_it.accounting.entry':
                self.accounting_entry_to_split = domain_ids
            return {
                'domain': {
                    'accounting_entry_to_split': [('id', 'in', domain_ids)]
                }
            }
        elif action == 'merge':
            return {
                'domain': {
                    'main_accounting_entry': [('id', 'in', domain_ids)]
                }
            }
        else:
            pass

    def _retrieve_domain_for_split_merge(self) -> list:
        """
        For split/merge action, the user should be specified what entry he want to split/merge.
        The splittable entry is the one that the user has selected from view list related to the account.move and
        to the l10n_it.accounting.entry models. This function return the ids to use in the domain for selected this
        entries.
        :return: ids list to use in domain
        """
        contextual_model = self._context['active_model']
        contextual_ids = self._context['active_ids']
        entry = self.env['l10n_it.accounting.entry']
        if contextual_model == 'l10n_it.accounting.entry':
            entry = self.env['l10n_it.accounting.entry'].browse(contextual_ids)
        elif contextual_model == 'account.move':
            move = self.env['account.move'].browse(contextual_ids)
            entry = move.mapped('accounting_entry_ids')
        elif contextual_model == 'account.move.line':
            move_lines = self.env['account.move.line'].browse(contextual_ids)
            entry = move_lines.mapped('accounting_entry_id')
        else:
            ValidationError(_(
                "This function is not expected for this model %s" % contextual_model
            ))
        return entry.ids

    def process_entries(self):
        self.ensure_one()
        action = self._context['action']
        if action == 'merge':
            move_lines = self._get_move_lines_to_merge()
            if not self.main_accounting_entry:
                raise ValidationError(_(
                    "Please specify the main accounting entry"
                ))
            result_entry = self.env['l10n_it.accounting.entry'].join_accounting_entry(
                move_lines,
                accounting_entry=self.main_accounting_entry
            )
        elif action == 'split':
            entries = self.accounting_entry_to_split
            move_lines = entries.mapped('accounting_entry_lines')
            if self._context['active_model'] == 'account.move':
                # If split option comes from account.move I have to considering only selected moves.
                context_move = self.env['account.move'].browse(self._context['active_ids'])
                move_lines = move_lines.filtered(lambda l: l.id in context_move.line_ids.ids)
            result_entry = self.env['l10n_it.accounting.entry'].split_accounting_entry(move_lines)
            entries.remove_orphan_accounting_entries()
        else:
            raise ValidationError("Unrecognized action (split/merge)")
        # Return the result
        action = self.env.ref('l10n_it_accounting_entry.action_open_l10n_it_accounting_entry').read()[0]
        if len(result_entry) > 1:
            action['domain'] = [('id', 'in', result_entry.ids)]
        else:
            action['res_id'] = result_entry.id
            action['view_mode'] = 'form'
            action['views'] = [(False, 'form')]
        return action

    @api.returns('account.move', lambda value: value.id)
    def _get_move_lines_to_merge(self):
        contextual_model = self._context['active_model']
        contextual_ids = self._context['active_ids']
        moves_lines = self.env['account.move.line']
        if contextual_model == 'l10n_it.accounting.entry':
            entries = self.env['l10n_it.accounting.entry'].browse(contextual_ids)
            moves_lines = entries.mapped('accounting_entry_lines')
        elif contextual_model == 'account.move':
            moves = self.env['account.move'].browse(contextual_ids)
            moves_lines = moves.mapped('line_ids')
        elif contextual_model == 'account.move.line':
            moves_lines = self.env['account.move.line'].browse(contextual_ids)
        else:
            pass
        return moves_lines
