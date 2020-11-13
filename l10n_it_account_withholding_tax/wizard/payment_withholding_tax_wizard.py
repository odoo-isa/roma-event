# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, RedirectWarning
from odoo.tools import float_is_zero
from logging import getLogger
from odoo.tools import float_compare

_logger = getLogger(__name__)


class PaymentWithholdingTax(models.TransientModel):
    _name = 'payment.withholding.tax.wizard'
    _description = 'Payment for Withholding Tax'

    account_id = fields.Many2one(
        string='Account',
        required=True,
        readonly=False,
        comodel_name='account.account',
        help='''Set this field with the accounting account for which the transaction is registered.''',
        copy=False,
        domain=[('user_type_id.type', '=', 'liquidity')]
    )

    date = fields.Date(
        string='Date',
        help='Date set on the accounting registration.',
        copy=False,
        default=fields.Date.today,
        required=True
    )

    def create_payment(self):
        if 'active_ids' in self.env.context:
            selected_ids = self.env.context.get('active_ids', False)
            acc_move_line_ids = self.env['account.move.line'].browse(selected_ids)
            # The move should be of withholding tax type
            acc_move_line_ids.mapped('move_id.is_withholding_tax')
            if not all(acc_move_line_ids):
                raise ValidationError(_("The move should be of withholding type"))
            # Only to paid
            currency = acc_move_line_ids.mapped('move_id.company_id.currency_id')
            if not currency:
                raise ValidationError(_("Unable to find a valid currency for this move."))
            currency = currency[0]
            prec_digits = currency.decimal_places
            acc_move_line_ids = acc_move_line_ids.filtered(
                lambda l: not float_is_zero(l.amount_residual, prec_digits)
            )
            to_reconcile = []
            move_id = self.create_move_id_for_payment(acc_move_line_ids)
            for move in acc_move_line_ids:
                if not float_is_zero(move.debit, prec_digits):
                    debit = 0
                    credit = move.debit
                else:
                    debit = move.credit
                    credit = 0
                move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'account_id': move.account_id.id,
                    'debit': debit,
                    'credit': credit,
                    'date': move.date,
                    'partner_id': move.partner_id.id if move.partner_id else False,
                    'move_id': move_id.id
                })
                to_reconcile.append(move + move_line)
            move_id.post()
            # Reconcile the moves of withholding payment
            for move_to_reconcile in to_reconcile:
                move_to_reconcile.reconcile()
            vals = {
                'name': move_id.name,
                'date': self.date,
                'move_id': move_id.id,
                'origin_move_line_ids': [(6, 0, acc_move_line_ids.ids)]
            }
            res_id = self.env['l10n_it.payment.withholding.tax'].create(vals)
            tree_id = self.env.ref('l10n_it_account_withholding_tax.l10n_it_payment_withholding_tax_tree').id
            form_id = self.env.ref('l10n_it_account_withholding_tax.l10n_it_payment_withholding_tax_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Generated Payments'),
                'res_model': 'l10n_it.payment.withholding.tax',
                'view_mode': 'tree,form',
                'views': [(tree_id, 'tree'), (form_id, 'form')],
                'domain': [('id', 'in', res_id.ids)],
            }

    def create_move_id_for_payment(self, move_lines):
        total = sum(line.credit - line.debit for line in move_lines)
        rounding = move_lines[0].product_uom.rounding
        # Cannot create negative withholding payment
        if float_compare(total, 0, precision_rounding=rounding) < 0:
            raise ValidationError(_("Unable to create a withholding payment with negative value."))
        date = move_lines[0].date
        ref = move_lines[0].move_id.name
        # If total is greater than 0, this value must be on debit column
        if total > 0:
            debit_line = {
                'account_id': self.account_id.id,
                'debit': 0,
                'credit': abs(total),
                'date': date,
                'partner_id': False,
            }
        # If total is smaller than 0, this value must be on credit column
        else:
            debit_line = {
                'account_id': self.account_id.id,
                'debit': abs(total),
                'credit': 0,
                'date': date,
                'partner_id': False,
            }
        withholding_journal = self.env.company.withholding_journal_id
        if not withholding_journal:
            action = self.env.ref('account.action_account_config')
            msg = _(
                'Cannot find parameter for the withholding tax, You should configure it. '
                '\nPlease go to Account Configuration.')
            raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
        move_id = self.env['account.move'].with_context(check_move_validity=False).create({
            'date': fields.Date.today(),
            'journal_id': withholding_journal.id,
            'state': 'draft',
            'line_ids': [(0, 0, debit_line)],
            'ref': _(f"Withholding deposit {ref}")
        })
        return move_id
