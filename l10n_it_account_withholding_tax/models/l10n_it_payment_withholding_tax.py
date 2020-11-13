# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class L10nItPaymentWithholdingTax(models.Model):
    _name = 'l10n_it.payment.withholding.tax'
    _description = 'Payment for Withholding Tax'

    name = fields.Char(
        string='Name',
        required=False,
        readonly=True
    )

    move_id = fields.Many2one(
        string='Move',
        required=False,
        readonly=False,
        index=False,
        default=None,
        comodel_name='account.move',
    )

    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        related="move_id.company_id",
        readonly=True,
        store=True
    )

    date = fields.Date(
        string='Date',
        copy=False,
    )

    origin_move_line_ids = fields.One2many(
        string='Origin Move Lines',
        readonly=True,
        comodel_name='account.move.line',
        inverse_name='l10n_it_payment_withholding_tax_id',
        help='''List of account move lines that has generate the payment of withholding tax.''',
        copy=False,
    )

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('l10n_it.payment.withholding.tax') or _('New')
        })
        return super(L10nItPaymentWithholdingTax, self).create(vals)

    def cancel_payment_withholding_tax(self):
        """
        Function that cancel the account move linked to the withholding payment then delete it from the database.
        :return: action window to the tree of withholding payment
        """
        for record in self:
            move_id = record.move_id
            move_id = move_id.with_context(avoid_withholding_pay_check=True,avoid_cancel_move=True)
            move_id.line_ids.remove_move_reconcile()
            move_id.button_cancel()
            record.unlink()
        tree_id = self.env.ref('l10n_it_account_withholding_tax.l10n_it_payment_withholding_tax_tree').id
        form_id = self.env.ref('l10n_it_account_withholding_tax.l10n_it_payment_withholding_tax_form').id
        return {
                'type': 'ir.actions.act_window',
                'name': _('Generated Payments'),
                'res_model': 'l10n_it.payment.withholding.tax',
                'view_mode': 'tree,form',
                'target': 'main',
                'flags': {
                    'headless': False,
                },
                'views': [(tree_id, 'tree'), (form_id, 'form')],
            }
