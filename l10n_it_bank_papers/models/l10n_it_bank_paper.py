# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger
from odoo.exceptions import ValidationError


_logger = getLogger(__name__)


class L10nItBankPaper(models.Model):
    _name = "l10n_it.bank_paper"
    _description = "Bank Paper"

    type = fields.Selection(
        string='Type',
        default="cash_order",
        selection=[('cash_order', 'Ca.Or/Ri.Ba')],
        help="Type",
        copy=True
    )

    document_reference = fields.Char(
        string='Document Reference',
        readonly=True,
        copy=True
    )

    document_date = fields.Char(
        string='Document Date',
        readonly=True,
        copy=True
    )

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        copy=True
    )

    partner_bank_id = fields.Many2one(
        string='Partner Bank',
        readonly=True,
        comodel_name='res.partner.bank',
        copy=True
    )

    iban = fields.Char(
        string='Iban',
        readonly=True,
        help="Res Partner Bank",
        copy=True
    )

    amount = fields.Float(
        string='Amount',
        index=False,
        default=0.0,
        copy=True
    )

    expiration_date = fields.Date(
        string='Expiration Date',
        copy=True
    )

    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('sent', 'Sent'), ('accepted', 'Accepted'), ('credited', 'Credited'), ('unpaid', 'Unpaid'), ('canceled', 'Canceled')],
        copy=True
    )

    account_move_line_ids = fields.One2many(
        string='Account Move Line',
        readonly=True,
        comodel_name='account.move.line',
        inverse_name='bank_paper_id',
        help="Account move lines for one bank paper",
        copy=True
    )

    acceptance_move_id = fields.Many2one(
        string='Acceptance Move',
        readonly=True,
        comodel_name='account.move',
        copy=True
    )

    bank_paper_id = fields.Many2one(
        string='Bank paper slip',
        comodel_name='l10n_it.bank_paper.slip',
        ondelete="cascade",
        help="Bank paper slip reference",
        copy=True
    )

    unsolved_move_id = fields.Many2one(
        string='Unsolved Move',
        help=False,
        comodel_name='account.move',
    )

    company_id = fields.Many2one(
        string='Company',
        compute="_get_bank_paper_info",
        comodel_name='res.company',
        store=True,
        copy=True
    )

    currency_id = fields.Many2one(
        string='Currency',
        compute="_get_bank_paper_info",
        store=True,
        comodel_name='res.currency',
        copy=True
    )

    company_currency_id = fields.Many2one(
        string='Company Currency',
        compute="_get_bank_paper_info",
        store=True,
        comodel_name='res.currency',
        copy=True
    )

    seq_bank_paper = fields.Integer(
        string='Seq Bank Paper',
        help="Sequence number of bank paper lines",
        copy=False
    )

    @api.depends('account_move_line_ids')
    def _get_bank_paper_info(self):
        for record in self:
            if record.account_move_line_ids:
                record.company_id = record.account_move_line_ids[0].company_id
                record.currency_id = record.account_move_line_ids[0].currency_id
                record.company_currency_id = record.account_move_line_ids[0].company_currency_id

    def record_unsolved(self):
        """
        Open wizard to show summary of account move is going to create for unsolved
        :return:
        """
        self.ensure_one()
        amount = self.amount
        if amount == 0:
            raise ValidationError(_("It's not possible to continue because amount is 0"))
        bank_paper_slip_type = self.bank_paper_id.bank_paper_slip_type_id
        bank_paper_slip_accreditation_wizard_id = self.env['l10n_it.bank_paper.slip.summary.wizard'].create({
            'journal_id': bank_paper_slip_type.credit_journal_id.id if bank_paper_slip_type.credit_journal_id else None,
            'account_id': bank_paper_slip_type.unpaid_bank_papers_credit_account_account_id.id if bank_paper_slip_type.unpaid_bank_papers_credit_account_account_id else self.partner_id.property_account_receivable_id.id,
            'bank_account_id': bank_paper_slip_type.bank_credit_account_account_id.id if bank_paper_slip_type.bank_credit_account_account_id else None,
            'bank_expense_account_id': bank_paper_slip_type.bank_charges_credit_account_account_id.id if bank_paper_slip_type.bank_charges_credit_account_account_id else None,
            'amount': amount,
            'bank_amount': amount,
            'expense_amount': 0
        })
        view_id = self.env.ref('l10n_it_bank_papers.view_bank_paper_unsolved_summary_form').id
        partner_bank = None
        if self.partner_id.bank_ids:
            partner_bank = self.partner_id.bank_ids.filtered(lambda l:l.default)
        if not partner_bank:
            partner_bank = self.partner_id.bank_ids[0]
        return {
            'name': _("Bank Paper Unsolved Summary"),
            'type': 'ir.actions.act_window',
            'res_model': 'l10n_it.bank_paper.slip.summary.wizard',
            'views': [(view_id, 'form'), (False, 'tree')],
            'res_id': bank_paper_slip_accreditation_wizard_id.id,
            'target': 'new',
            'context': {
                        'default_partner_bank_id': partner_bank.id,
                        'partner_id': self.partner_id.id}
        }
