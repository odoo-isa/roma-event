# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class L10nItBankPaperSlipTypes(models.Model):
    _name = 'l10n_it.bank_paper.slip.types'
    _description = 'Bank Paper Slip Types'

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
    )

    type = fields.Selection(
        string='Type',
        required=True,
        readonly=True,
        default='cash_order',
        selection=[('cash_order', 'Ca.Or.')],
        help='Field used to define the type of the bank paper. Actually is define only Cash Order type.',
        copy=False,
    )

    slip_type = fields.Selection(
        string='Slip Type',
        required=True,
        readonly=False,
        default='sbf',
        selection=[('sbf', 'Under Reserve')],
        help='Field used to define the type of the bank paper slip. Possible value is SBF - Under Reserve',
        copy=False,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
        copy=False,
    )

    company_bank_account_id = fields.Many2one(
        string='Company Bank Account',
        required=True,
        readonly=False,
        comodel_name='res.partner.bank',
        domain=[('id', 'in', lambda self: self.company_id.partner_id.bank_ids.ids)],
        help='With this field is possible to set a company bank account',
        copy=False,
    )

    # Acceptance Fields

    acceptance_journal_id = fields.Many2one(
        string='Acceptance Journal',
        required=True,
        readonly=False,
        comodel_name='account.journal',
        domain=[('type', '=', 'bank')],
        help='Acceptance Journal',
        copy=False,
    )

    bank_papers_acceptance_account_account_id = fields.Many2one(
        string='Acceptance - Bank Papers Account',
        required=True,
        readonly=False,
        comodel_name='account.account',
        domain=[('related_account_type', '=', 'receivable')],
        help='Company Bank Account',
        copy=False
    )

    # Accreditation Field

    credit_journal_id = fields.Many2one(
        string='Credit Journal',
        required=False,
        readonly=False,
        comodel_name='account.journal',
        domain=[('type', '=', 'bank')],
        help='',
        copy=False,
    )

    bank_papers_credit_account_account_id = fields.Many2one(
        string='Credit - Bank Papers Account',
        required=False,
        readonly=False,
        comodel_name='account.account',
        help='',
        copy=False,
    )

    bank_credit_account_account_id = fields.Many2one(
        string='Bank Account',
        required=False,
        readonly=False,
        comodel_name='account.account',
        domain=[('related_account_type', '=', 'liquidity')],
        help='',
        copy=False,
    )

    bank_charges_credit_account_account_id = fields.Many2one(
        string='Bank Charges Account',
        required=False,
        readonly=False,
        index=False,
        default=None,
        comodel_name='account.account',
        help='',
        copy=False,
    )

    # Unsolved Move Fields

    unpaid_bank_papers_journal_id = fields.Many2one(
        string='Unpaid Bank Papers Journal',
        required=False,
        readonly=False,
        comodel_name='account.journal',
        domain=[('type', '=', 'bank')],
        help='',
        copy=False,
    )

    unpaid_bank_papers_credit_account_account_id = fields.Many2one(
        string='Unpaid Bank Papers Account',
        required=False,
        readonly=False,
        comodel_name='account.account',
        domain=[('related_account_type', '=', 'receivable')],
        help='',
        copy=False,
    )

    unpaid_bank_papers_charges_account_account_id = fields.Many2one(
        string='Unpaid Bank Papers Charges Account',
        required=False,
        readonly=False,
        index=False,
        default=None,
        comodel_name='account.account',
        help='',
        copy=False,
    )

    bank_unpaid_bank_papers_account_account_id = fields.Many2one(
        string='Bank Account unpaid',
        required=False,
        readonly=False,
        comodel_name='account.account',
        domain=[('related_account_type', '=', 'liquidity')],
        help='',
        copy=False,
    )

    @api.onchange('company_id')
    def onchange_company_bank_account_id(self):
        if self.company_id:
            return {'domain': {'company_bank_account_id': [('id', 'in', self.company_id.partner_id.bank_ids.ids)]}}
