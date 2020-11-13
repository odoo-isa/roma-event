# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    def create_tax_cash_basis_entry(self, percentage_before_rec):
        """
        This function inherit the standard cause of a wrong compute of cahs besis entry line.
        In standard function, the goods account was be considering as exigible on payment. This behavior is fixed
        by this function. Before to call super we change the flag tax_exigible to true for the goods account move line.
        /!\ this behavior is correct also in case of withholding tax but, in this case, the function call another
        function (have a look inside l10n_it_account_withholding_tax module)
        :param percentage_before_rec:
        :return:
        """
        self.ensure_one()
        # Retrieve all transit account for payment exigibility
        transit_account_tax = self.env['account.tax'].search([
            ('tax_exigibility', '=', 'on_payment'),
            ('cash_basis_transition_account_id', '!=', False)
        ])
        transit_account = transit_account_tax.mapped('cash_basis_transition_account_id')
        for move in {self.debit_move_id.move_id, self.credit_move_id.move_id}:
            lines_should_exigible = move.line_ids.filtered(
                lambda l: not l.tax_exigible and l.account_id not in transit_account
            )
            if lines_should_exigible:
                lines_should_exigible.write({
                    'tax_exigible': True
                })
        return super(AccountPartialReconcile, self).create_tax_cash_basis_entry(percentage_before_rec)
