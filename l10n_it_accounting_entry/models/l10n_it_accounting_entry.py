# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class L10nItAccountingEntry(models.Model):
    _name = 'l10n_it.accounting.entry'
    _description = 'Accounting Entry'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Name',
        required=True,
        help='The name of the accounting entry. This is an unique name.',
        copy=False
    )

    display_name = fields.Char(
        string='Display name',
        compute="_compute_display_name",
        store=True,
        help='''Using for display name of the accounting entry''',
        copy=False,
    )

    partner_id = fields.Many2one(
        string='Partner',
        readonly=True,
        comodel_name='res.partner',
        ondelete="restrict",
        help='''The partner of this accounting entry. Can be null''',
    )

    account_id = fields.Many2one(
        string='Account',
        readonly=True,
        comodel_name='account.account',
        ondelete="restrict",
        help='''The account of this accounting entry''',
    )

    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        readonly=True,
        compute="_compute_company",
        store=True,
        index=True,  # It is used for access rule searching.
    )

    accounting_entry_lines = fields.One2many(
        string='Account Move Lines',
        required=False,
        readonly=True,
        comodel_name='account.move.line',
        inverse_name='accounting_entry_id',
        help='All the move line that compose the accounting entry',
        copy=False,
    )

    amount = fields.Float(
        string='Amount',
        compute='_get_accounting_entry_amount',
        store=True,
        required=False,
        readonly=True,
        default=0.0,
        digits='Product Price',
        help='This field contains the amount of the accounting entry, computed as the difference in absolute value '
             'between the debit and credit of all the accounting movements linked to the accounting entry. It is used '
             'to define the state of the accounting entry.',
        copy=False,
    )

    state = fields.Selection(
        string='State',
        compute='_get_accounting_entry_amount',
        store=True,
        required=False,
        readonly=True,
        selection=[('open', 'Open'), ('close', 'Close')],
        help='The field indicates the status of the accounting item: when the state is open it means that the sum of '
             'the Debit and Credit of the accounting records related to the accounting entry is not currently balanced;'
             ' if instead it is equal to 0 then the accounting entry is considered closed and the amounts balanced.',
        copy=False,
    )

    '''=== Compute method ==='''
    @api.depends('accounting_entry_lines', 'accounting_entry_lines.parent_state')
    def _get_accounting_entry_amount(self):
        """
        Compute the amount and the state of the accounting entry
        :return: void
        """
        for entry in self:
            entry_line = entry.accounting_entry_lines.filtered(lambda l: l.parent_state == 'posted')
            if not entry_line:
                continue
            amount_debit = sum(entry_line.mapped('debit'))
            amount_credit = sum(entry_line.mapped('credit'))
            company = entry.company_id
            if not company:
                company = entry.mapped('accounting_entry_lines.company_id')[0]
            entry.amount = amount_debit - amount_credit
            if float_is_zero(entry.amount, precision_rounding=company.currency_id.rounding):
                entry.state = 'close'
            else:
                entry.state = 'open'

    @api.depends('accounting_entry_lines')
    def _compute_company(self):
        """
        This function compute the company of the accounting entry. The company is retrieved from the account move line.
        The account move line must have same company because the constraint check for it.
        :return: void
        """
        for entry in self:
            if not entry.accounting_entry_lines:
                continue
            company_id = entry.mapped('accounting_entry_lines.company_id')
            if len(company_id) > 1:  # There is a constraint for that
                continue
            entry.company_id = company_id.id

    @api.depends('partner_id', 'name')
    def _compute_display_name(self):
        for entry in self:
            entry.display_name = entry.name
            if entry.partner_id:
                entry.display_name = "%s (%s)" % (entry.name, entry.partner_id.name)

    '''=== Constraints ==='''
    @api.constrains('accounting_entry_lines')
    def _check_same_company(self):
        """
        This function search for same company in the same accounting entry
        :raise: ValidationError if multi company for the same accounting entry
        :return: void
        """
        for entry in self:
            if len(entry.mapped('accounting_entry_lines.company_id.id')) > 1:
                raise ValidationError(_(
                    "The account move line of this account entry must to have the same company. "
                    "Unable to have multi company on the same accounting entry."
                ))

    @api.constrains('accounting_entry_lines')
    def _check_same_partner_account(self):
        for entry in self:
            partner = entry.mapped('accounting_entry_lines.partner_id')
            account = entry.mapped('accounting_entry_lines.account_id')
            if len(partner) > 1:
                raise ValidationError(_(
                    "Unable to have the same accounting entry for more than one partner."
                ))
            if len(account) > 1:
                raise ValidationError(_(
                    "Unable to have the same accounting entry for different account."
                ))

    _sql_constraints = [(
        'name_partner_account_uniq', 'unique(name, partner_id, account_id)',
        "Statement must be unique by name account and partner."
    )]

    '''=== Utilities method ==='''

    def generate_accounting_entry(self, tuple_data, move_lines=None):
        """
        This function generate the accounting entry
        :param tuple_data: the tuple contains data. Tuple structure:
            [0] - the move (must be one) from which retrieve some data (example the entry name)
            [1] - the partner
            [2] - rest unused data group.
        :param move_lines: Optional argument, the move lines to link to this accounting entry
        :return: The generated accounting entry
        """
        move_id, *rest = tuple_data
        move_id.ensure_one()
        accounting_entry = self._retrieve_existing_accounting_entry(tuple_data)
        if accounting_entry:
            move_lines.write({
                'accounting_entry_id': accounting_entry.id
            })
        else:
            values = self._generate_entry_values(tuple_data, move_lines)
            accounting_entry = self.env['l10n_it.accounting.entry'].create(values)
        return accounting_entry

    @staticmethod
    def _generate_entry_values(tuple_data: tuple, move_lines) -> dict:
        """
        :param tuple_data: tuple of data
            [0] - the move (must be one) from which retrieve some data (example the entry name)
            [1] - the partner
            [2] - rest unused data group.
        :param move_lines: lines to link to the accounting entries
        """
        move, partner, account_id, *rest = tuple_data
        values = {
            'name': move.name,
            'partner_id': partner.id,
            'account_id': account_id.id,
        }
        if move_lines:
            values['accounting_entry_lines'] = [(6, 0, move_lines.ids)]
        return values

    def _retrieve_existing_accounting_entry(self, tuple_data: tuple):
        """
        Search for existing accounting entry
        :param tuple_data: the key data
        :return: The founded accounting entry
        """
        domain = self._get_key_search_domain(tuple_data)
        accounting_entry = self.search(domain, limit=1)
        if accounting_entry:
            return accounting_entry
        return self.env['l10n_it.accounting.entry']  # return empty object

    @staticmethod
    def _get_key_search_domain(tuple_data: tuple) -> list:
        """
        Generate domain for search existing accounting entries
        :param tuple_data: the key data
        :return: list of domain
        """
        domain = []
        move, partner, account_id, *rest = tuple_data
        domain = expression.AND([domain, [
            ('name', '=', move.name),
            ('account_id', '=', account_id.id)
        ]])
        if partner:
            domain = expression.AND([domain, [('partner_id', '=', partner.id)]])
        else:
            domain = expression.AND([domain, [('partner_id', '=', False)]])
        return domain

    def join_accounting_entry(self, move_lines, accounting_entry=None):
        """
        This function is used to join the accounting entries in the move line in only one accounting entry.
        Other entries will be removed if necessary (if this one don't have no more lines).
        The main entry will be retrieved using a priority mechanism. The priority mechanism search for (in order of
        priority):
            1 - Search for the invoice in move lines (equal treatment considering the one with lowest date)
            2 - Search for refund in move lines (equal treatment considering the one with lowest date)
            3 - Considering the move line with lowest date.
        :param move_lines:The move line from which join the accounting entry
        :param accounting_entry: If passed, will be considering this accounting entry instead of retrieving one with the
        priority mechanism.
        :return:
        """
        # Obviously considering only moves that has accounting entry
        entry_move_lines = move_lines.filtered(lambda l: l.accounting_entry_id)
        if not entry_move_lines:
            return self.env['l10n_it.accounting.entry']  # return empty object
        if accounting_entry:
            main_entry_line = move_lines.filtered(lambda l: l.accounting_entry_id == accounting_entry)
            if not main_entry_line:
                raise ValidationError(_(
                    "The accounting entry %s could not be found" % (accounting_entry.name,)
                ))
            main_entry_line = main_entry_line
        else:
            main_entry_line = self._get_main_entry_line(entry_move_lines)
        main_entry_line = main_entry_line
        # Merge the statement for all the move
        (entry_move_lines - main_entry_line).write({
            'accounting_entry_id': main_entry_line.accounting_entry_id.id
        })
        return main_entry_line.accounting_entry_id

    def remove_orphan_accounting_entries(self):
        to_delete = self.filtered(lambda e: not e.accounting_entry_lines)
        if to_delete:
            to_delete.unlink()

    @staticmethod
    def _get_main_entry_line(entry_move_lines):
        """
        Retrieve the main entry based to the priority mechanism.
        :param entry_move_lines: line with statement id
        :return: main entry line (account move line with the main accounting entry)
        """
        # 1 attempt - Search for invoice
        main_entry_line = entry_move_lines.filtered(
            lambda l: l.move_id.type in ('out_invoice', 'in_invoice', 'in_receipt', 'out_receipt')
        )
        # 2 attempt - Search for refund move
        if not main_entry_line:
            main_entry_line = entry_move_lines.filtered(
                lambda l: l.move_id.type in ('in_refund', 'out_refund')
            )
        # 3 - search entry linked with invoice
        if not main_entry_line:
            # Search for entry linked to move that is invoice
            entry_of_invoice = entry_move_lines.mapped('accounting_entry_id').filtered(
                    lambda statement: statement.accounting_entry_lines.filtered(
                        lambda move_line: move_line.move_id.is_invoice()
                    )
                )
            main_entry_line = entry_move_lines.filtered(
                lambda m: m.accounting_entry_id in entry_of_invoice
            )
        # 4 - considering by date.
        if not main_entry_line:
            main_entry_line = entry_move_lines
        main_entry_line = main_entry_line.sorted(key=lambda l: l.move_id.date)[0]
        return main_entry_line

    def split_accounting_entry(self, move_lines):
        """
        This function divide thr accounting entries for the move lines. This function is useful during the account move
        line unreconciliation.
        :param move_lines: the move line for recompute the original accounting entries
        :return: True
        """
        # Prepare the collection of entry to return
        res = self.env['l10n_it.accounting.entry']
        # Retrieve the main entry line. The accounting_entry of the main entry account will not be recompute
        main_entry_line = self._get_main_entry_line(move_lines)
        main_entry = main_entry_line.accounting_entry_id
        # Retrieve all the lines linked to the main entry line
        main_entry_lines = main_entry_line.move_id.line_ids
        # Remove from the move_lines the main_entry_lines so the account_entry will not be recompute. Use set to avoid
        # redundant data
        move_lines = set(move_lines - main_entry_lines)
        if not move_lines:
            raise ValidationError(_("Unable to find entry to split"))
        # Check if for move already exist accounting_entry, otherwise I have to regenerate
        move_lines = self.env['account.move.line'].browse([x.id for x in move_lines])
        # Create a collection of move for which assign the entry automatically
        entry_move_line_to_assign = move_lines
        for line in move_lines:
            entry_to_assign = line.move_id.line_ids.filtered(
                lambda l: l.accounting_entry_id and l.accounting_entry_id != main_entry
            )
            if not entry_to_assign:
                continue
            # Only accounting_entry with same account
            entry_to_assign = entry_to_assign.filtered(lambda e: e.account_id == line.account_id)
            if not entry_to_assign:
                continue
            entry_to_assign = entry_to_assign[0].accounting_entry_id
            res += entry_to_assign
            line.accounting_entry_id = entry_to_assign.id
            entry_move_line_to_assign -= line
        if entry_move_line_to_assign:
            entry_move_line_to_assign.update({
                'accounting_entry_id': None
            })
        res += move_lines.shall_assign_accounting_entry()
        return res
