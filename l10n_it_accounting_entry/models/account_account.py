# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = "account.account"

    managed_by_accounting_entry = fields.Boolean(
        string='Managed by Accounting Entry',
        help='The account is subjected to the accounting entry management',
        copy=False,
    )

    @api.onchange('user_type_id')
    def onchange_user_type_id(self):
        """
        Suggest managed by account entry flag if account type is payable or receivable
        :return:
        """
        if self.user_type_id.type in ('payable', 'receivable'):
            self.managed_by_accounting_entry = True
        else:
            self.managed_by_accounting_entry = False
