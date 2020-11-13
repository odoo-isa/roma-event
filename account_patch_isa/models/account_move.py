# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_mode = fields.Selection(
        string='Invoice Mode',
        required=True,
        help="Invoice type,changes if the invoice is created immediately, after the creation of the delivery note etc.",
        selection=[('immediate', 'Immediate invoice')],
        default='immediate'

    )

    # This field is adding to show, if present, account move that was generated from this one with exigibility on
    # payment. This is useful for cash flow or withholding tax
    moves_deferred_exigibility = fields.Many2many(
        string="Deferred exigibility",
        comodel_name="account.move",
        compute="_get_deferred_exigibility_moves"
    )

    count_deferred_exigibility = fields.Integer(
        string='# of exigibility moves',
        compute="_get_deferred_exigibility_moves"
    )

    def _get_deferred_exigibility_moves(self):
        for move in self:
            partial_reconcile = self.env['account.partial.reconcile'].search([
                '|', ('debit_move_id', 'in', move.line_ids.ids),
                ('credit_move_id', 'in', move.line_ids.ids)
            ])
            deferred_exigibility_move = self.env['account.move'].search([
                ('tax_cash_basis_rec_id', 'in', partial_reconcile.ids)
            ])
            move.moves_deferred_exigibility = deferred_exigibility_move.ids
            move.count_deferred_exigibility = len(deferred_exigibility_move)

    def view_deferred_tax_exigibility(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        deferred_move = self.moves_deferred_exigibility
        action.update({
            'name': self.name,
            'domain': [('id', 'in', deferred_move.ids)],
        })
        if len(deferred_move) == 1:
            action['res_id'] = deferred_move.id
            action['views'] = [(False, 'form')]
        return action

    @api.model
    def create(self, vals):
        """
        It's made a change about account move line sequence number: instead starting them from 0, they're will start
        from 1. This is for the correct behavior in the xml invoice.
        :param vals: Dict
        :return: Recordset
        """
        res_id = super(AccountMove, self).create(vals)
        seq = 1
        for invoice_line in res_id.invoice_line_ids:
            invoice_line.sequence = seq
            seq += 1
        return res_id

    def post_create(self, invoices, references):
        """
        Function that can be invoked after that an invoice it was created.
        This function can be useful when was create a batch invoice (without passing from UI) so the compute fields
        should be recomputes.
        The recompute algorithm is based to the Odoo function "_create_invoices". This function create invoice and
        compute total all in one single monolithic function. We have extract the part of code that is responsible for
        the computation.
        :param invoices: The invoices for which recompute total
        :param references: If invoice it was created from another document this will be post in the invoice's thread.
        :return:
        """
        if not invoices:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        for invoice in invoices.values():
            invoice._recompute_tax_lines()
            if not invoice.invoice_line_ids:
                raise UserError(_(
                    'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice._recompute_tax_lines()
            # Idem for partner
            so_payment_term_id = invoice.invoice_payment_term_id.id
            fp_invoice = invoice.fiscal_position_id
            set_partner_shipping = self._context.get('set_partner_shipping', None)
            partner_shipping_id = None
            if set_partner_shipping:
                partner_shipping_id = invoice.partner_shipping_id
            invoice.with_context(set_partner_shipping=set_partner_shipping, partner_shipping_id=partner_shipping_id)._onchange_partner_id()
            invoice.fiscal_position_id = fp_invoice
            # To keep the payment terms set on the SO
            invoice.payment_term_id = so_payment_term_id
            invoice.message_post_with_view('mail.message_origin_link',
                                           values={'self': invoice, 'origin': references[invoice]},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        return

    """
    ====================================================================================================================
    * OVERRIDE FUNCTIONS for payment term computation line on invoice                                                  *
    ====================================================================================================================
    """
    def _recompute_payment_terms_lines(self):
        """
        Compute the dynamic payment term lines of the journal entry. This function is copied from the standard function
        of Odoo. We need to rewrite it because in the standard function there are sub-functions that cannot be inherit.
        The only solution is to transform the sub-functions in method functions put these outside of the function
        _recompute_payment_terms_lines and transform these one as method. These function are:
         * _get_payment_terms_computation_date
         * _get_payment_terms_account
         * _compute_payment_terms
         * _compute_diff_payment_terms_lines
        Together of this functions, we have provided also utility function that allow us to easily inherit to adding
        extra data (Eg. the payment_term). This function are:
         * _get_candidate
         * _alter_existing_term_lines
         * _alter_other_lines

        :return:
        """
        self.ensure_one()

        existing_terms_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        existing_terms_lines = self._alter_existing_term_lines(existing_terms_lines)
        others_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        others_lines = self._alter_other_lines(others_lines)
        company_currency_id = self.company_id.currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))

        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = self._get_payment_terms_computation_date()
        account = self._get_payment_terms_account(existing_terms_lines)
        to_compute = self._compute_payment_terms(computation_date, total_balance, total_amount_currency)
        new_terms_lines = self._compute_diff_payment_terms_lines(existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.invoice_payment_ref = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity

    def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
        ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
        :param self:                    The current account.move record.
        :param existing_terms_lines:    The current payment terms lines.
        :param account:                 The account.account record returned by '_get_payment_terms_account'.
        :param to_compute:              The list returned by '_compute_payment_terms'.
        '''
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        # As we try to update existing lines, sort them by due date.
        existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
        existing_terms_lines_index = 0

        # Recompute amls: update existing line or create new one for each payment term.
        new_terms_lines = self.env['account.move.line']
        for date_maturity, balance, amount_currency, kwargs in to_compute:
            if self.journal_id.company_id.currency_id.is_zero(balance) and len(to_compute) > 1:
                continue

            if existing_terms_lines_index < len(existing_terms_lines):
                # Update existing line.
                candidate = existing_terms_lines[existing_terms_lines_index]
                existing_terms_lines_index += 1
                candidate = self._get_candidate(candidate, date_maturity, balance, amount_currency,
                                                **kwargs)
            else:
                # Create new line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
                    'account.move.line'].create
                candidate = create_method(
                    self._create_account_move_lines(balance, amount_currency, date_maturity, account,
                                                    **kwargs))
            new_terms_lines += candidate
            if in_draft_mode:
                candidate._onchange_amount_currency()
                candidate._onchange_balance()
        return new_terms_lines

    def _get_candidate(self, candidate, date_maturity, balance, amount_currency, **kwargs):
        candidate.update({
            'date_maturity': date_maturity,
            'amount_currency': -amount_currency,
            'debit': balance < 0.0 and -balance or 0.0,
            'credit': balance > 0.0 and balance or 0.0,
        })
        return candidate

    def _create_account_move_lines(self, balance, amount_currency, date_maturity, account, **kwargs):
        return {
            'name': self.invoice_payment_ref or '',
            'debit': balance < 0.0 and -balance or 0.0,
            'credit': balance > 0.0 and balance or 0.0,
            'quantity': 1.0,
            'amount_currency': -amount_currency,
            'date_maturity': date_maturity,
            'move_id': self.id,
            'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
            'account_id': account.id,
            'partner_id': self.commercial_partner_id.id,
            'exclude_from_invoice_tab': True
        }

    def _compute_payment_terms(self, date, total_balance, total_amount_currency):
        ''' Compute the payment terms.
        :param self:                    The current account.move record.
        :param date:                    The date computed by '_get_payment_terms_computation_date'.
        :param total_balance:           The invoice's total in company's currency.
        :param total_amount_currency:   The invoice's total in invoice's currency.
        :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
        '''
        if self.invoice_payment_term_id:
            to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date,
                                                              currency=self.currency_id)
            if self.currency_id != self.company_id.currency_id:
                # Multi-currencies.
                to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency,
                                                                           date_ref=date,
                                                                           currency=self.currency_id)
                return [(b[0], b[1], ac[1], b[2] if b[2] else {}) for b, ac in zip(to_compute, to_compute_currency)]
            else:
                # Single-currency.
                return [(b[0], b[1], 0.0, b[2] if b[2] else {}) for b in to_compute]
        else:
            return [(fields.Date.to_string(date), total_balance, total_amount_currency, {})]

    def _get_payment_terms_account(self, payment_terms_lines):
        ''' Get the account from invoice that will be set as receivable / payable account.
        :param self:                    The current account.move record.
        :param payment_terms_lines:     The current payment terms lines.
        :return:                        An account.account record.
        '''
        if payment_terms_lines:
            # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
            return payment_terms_lines[0].account_id
        elif self.partner_id:
            # Retrieve account from partner.
            if self.is_sale_document(include_receipts=True):
                return self.partner_id.property_account_receivable_id
            else:
                return self.partner_id.property_account_payable_id
        else:
            # Search new account.
            domain = [
                ('company_id', '=', self.company_id.id),
                ('internal_type', '=',
                 'receivable' if self.type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
            ]
            return self.env['account.account'].search(domain, limit=1)

    def _get_payment_terms_computation_date(self):
        ''' Get the date from invoice that will be used to compute the payment terms.
        :param self:    The current account.move record.
        :return:        A datetime.date object.
        '''
        today = fields.Date.context_today(self)
        if self.invoice_payment_term_id:
            return self.invoice_date or today
        else:
            return self.invoice_date_due or self.invoice_date or today
    
    def _alter_existing_term_lines(self, existing_terms_lines):
        # By default this function doesn't change the set of existing term lines on the invoice
        return existing_terms_lines

    def _alter_other_lines(self, other_lines):
        # By default this function doesn't change the set of other lines on the invoice
        return other_lines

    """
    ====================================================================================================================
    * END OF OVERRIDE FUNCTIONS for payment term computation line on invoice                                           *
    ====================================================================================================================
    """
