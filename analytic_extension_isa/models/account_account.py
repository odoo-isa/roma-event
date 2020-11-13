# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    analytic_account_ids = fields.Many2many(
        string='Analytic account',
        comodel_name='account.analytic.account',
        relation='account_account_analytic_account_rel',
        column1='account_account_id',
        column2='analytic_account_id',
        help='''The account analytic account related to this account. The analytic account will  be mandatory in the 
        book entry.''',
        copy=False,
        groups="analytic.group_analytic_accounting"
    )

    is_mandatory_analytic_account = fields.Boolean(
        string='Analytic account mandatory',
        help='''System field that indicate id the analytic account is mandatory.''',
        compute="_compute_is_mandatory_analytic_account",
        store=True,
        groups="analytic.group_analytic_accounting"
    )

    user_has_analytic_group = fields.Boolean(
        string='The user has analytic group',
        help='''System field that indicate if the user has analytic group''',
        compute="_user_has_analytic_group",
        default="_user_has_analytic_group"
    )

    def _user_has_analytic_group(self):
        self.user_has_analytic_group = self.env.user.has_group('analytic.group_analytic_accounting')

    @api.depends('analytic_account_ids')
    def _compute_is_mandatory_analytic_account(self):
        for account in self:
            account.is_mandatory_analytic_account = len(account.analytic_account_ids) > 0

