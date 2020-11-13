# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    related_mandatory_analytic = fields.Boolean(
        string='Is mandatory analytic account',
        help='''Related field that indicate if analytic account is mandatory''',
        related="account_id.is_mandatory_analytic_account",
        groups="analytic.group_analytic_accounting",
    )

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        if self.analytic_tag_ids and self.analytic_account_id:
            self.analytic_tag_ids = None

    @api.onchange('analytic_tag_ids')
    def _onchange_analytic_tag_ids(self):
        if self.analytic_account_id:
            self.analytic_account_id = None

    @api.onchange('account_id')
    def _onchange_account_id_for_analytic(self):
        """
         - Clear analytic account if for account is a mandatory field
         - Set analytic account for mandatory account that have only one related analytic account
        :return: Void
        """
        if not self.user_has_groups('analytic.group_analytic_accounting'):
            return
        if self.account_id and self.related_mandatory_analytic:
            self.analytic_account_id = False
        if self.account_id and len(self.account_id.analytic_account_ids) == 1:
            self.analytic_account_id = self.account_id.analytic_account_ids.id
