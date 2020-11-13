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


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_it_payment_withholding_tax_id = fields.Many2one(
        string='Payment for Withholding Tax',
        required=False,
        readonly=False,
        index=False,
        default=None,
        comodel_name='l10n_it.payment.withholding.tax',
        help='This field show the linked payment for Withholding Tax.',
        copy=False,
    )

    @api.constrains('tax_ids')
    def check_tax_pension_fund(self):
        pension_fund_tax_list = []
        line_with_same_pension_fund_list = []
        line_to_check_tax = []
        for record in self:
            for line in record.move_id.invoice_line_ids:
                pension_fund_tax = line.tax_ids.filtered(lambda t: t.account_tax_type == 'cassa_previdenziale')
                if len(pension_fund_tax) > 1:
                    raise ValidationError(_(
                        "It's not possible to save because line %s has two security fund in taxes" % (line.name,)
                    ))
                elif pension_fund_tax:
                    pension_fund_tax_list.append(pension_fund_tax)
                else:
                    pass
            if pension_fund_tax_list:
                multiple_pension_fund_taxes = set(x for x in pension_fund_tax_list if pension_fund_tax_list.count(x) > 1)
                for line in record.move_id.invoice_line_ids:
                    if line.tax_ids.filtered(lambda t: t.account_tax_type == 'cassa_previdenziale') in multiple_pension_fund_taxes:
                        line_with_same_pension_fund_list.append(line)
                for line in line_with_same_pension_fund_list:
                    line_to_check_tax.append(line.tax_ids.filtered(lambda t: t.account_tax_type == 'vat_tax'))
                if not all(x == line_to_check_tax[0] for x in line_to_check_tax):
                    raise ValidationError(_("It's not possible to continue because there is lines with same pension "
                                            "fund and different taxes"))

    def get_move_payment_withholding_tax(self):
        tree_view_id = self.env.ref('l10n_it_account_withholding_tax.select_account_move_line_withholding_tax_tree').id
        form_view_id = self.env.ref("l10n_it_account_withholding_tax.select_account_move_line_withholding_tax_form").id
        transition_accounts = self.env['account.tax'].search([('account_tax_type', '=', 'withholding_tax')]).mapped(
            "cash_basis_transition_account_id.id")
        payment_withholding_tax = [('account_id.l10n_it_account_usage', '=', 'withholding_tax'),\
                                   ('amount_residual', '!=', 0),\
                                   ('parent_state', '=', 'posted'),\
                                   ('move_id.is_withholding_tax', '=', True),\
                                   ('account_id', 'not in', transition_accounts)]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'views': [(tree_view_id, 'list'), (form_view_id, 'form')],
            'view_mode': 'list',
            'target': 'current',
            'name': "Payment Account Withholding Tax",
            'domain': payment_withholding_tax,
            'context': {'group_by': ['date_maturity', 'move_id', 'tax_line_id']}
        }

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        if self.move_id.partner_id.withholding_tax_id and self.product_id.type == 'service':
           self.tax_ids = [(4, self.move_id.partner_id.withholding_tax_id.id, 0)]
        return res


