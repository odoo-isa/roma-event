# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    check_consistency_amount = fields.Boolean(
        string='Check Consist',
        help='Is true if amount of analytic line sum is the same of account move line amount, else False.',
        default=True,
        compute='_check_consistency_amount',
    )

    def _check_consistency_amount(self):
        for record in self:
            analytic_line_ids = record.move_id.analytic_line_ids
            analytic_line_ids_amount = sum([analytic_line_id.amount for analytic_line_id in analytic_line_ids])
            account_line_ids_amount = (-1) * record.move_id.balance
            if analytic_line_ids_amount == account_line_ids_amount:
                record.check_consistency_amount = True
            else:
                record.check_consistency_amount = False