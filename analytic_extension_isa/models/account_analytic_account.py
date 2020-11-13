# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.osv import expression
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    analytic_group_complete_name = fields.Char(
        string='Analytic Group name',
        help='''related fields that contains the complete name of the analytic group''',
        related="group_id.complete_name",
        store=True,
    )

    account_ids = fields.Many2many(
        string='Account',
        comodel_name='account.account',
        relation='account_account_analytic_account_rel',
        column1='analytic_account_id',
        column2='account_account_id',
        help='''The account linked to this analytic account.''',
        copy=False,
    )

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """
        Only the admitted analytic account if specified in account account
        """
        args = args or []
        if name:
            args = expression.AND([
                [('name', operator, name)],
                args
            ])
        if 'related_mandatory_analytic' in self._context:
            account_id = self._context['account_id']  # if account_id is not present in context have to raise exception
            if account_id and self._context['related_mandatory_analytic']:
                args = expression.AND([
                    [('account_ids', '=', account_id)]
                    ,
                    args
                ])
        return super(AccountAnalyticAccount, self)._name_search(name, args, operator, limit, name_get_uid)
