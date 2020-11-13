# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    accounting_entry_ids = fields.One2many(
        string='Accounting entries',
        comodel_name='l10n_it.accounting.entry',
        compute="_get_accounting_entries",
        help="List of all accounting entries linked to this move",
        readonly=True
    )

    accounting_entry_count = fields.Integer(
        string='# of Accounting entries',
        help='System field for count the number of the accounting entries',
        compute="_get_accounting_entries",
    )

    @api.depends('line_ids.accounting_entry_id')
    def _get_accounting_entries(self):
        """
        Get the accounting entries linked to this move
        :return: void
        """
        for move in self:
            move.accounting_entry_ids = move.line_ids.filtered(
                lambda l: l.accounting_entry_id
            ).mapped('accounting_entry_id')
            move.accounting_entry_count = len(move.accounting_entry_ids)

    def post(self):
        """
        Inherit the post function to generate the accounting entries
        """
        res = super(AccountMove, self).post()
        self.line_ids.shall_assign_accounting_entry()
        return res

    def open_accounting_entries(self):
        """
        View the accounting entries
        :return: ir act windows
        """
        self.ensure_one()
        action = self.env.ref('l10n_it_accounting_entry.action_open_l10n_it_accounting_entry').read()[0]
        if self.accounting_entry_count > 1:
            action['domain'] = [('id', 'in', self.accounting_entry_ids.ids)]
        else:
            action['res_id'] = self.accounting_entry_ids.id
            action['view_mode'] = 'form'
            action['views'] = [(False, 'form')]
        return action
