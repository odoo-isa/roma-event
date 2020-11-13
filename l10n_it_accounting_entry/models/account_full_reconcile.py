# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"

    def create(self, vals_list):
        """
        When two move line is matching we have to assign the same accounting entry for both of then.
        :param vals_list: value list to write vals_list
        :return: account full reconcile object
        """
        res = super(AccountFullReconcile, self).create(vals_list)
        # We have to assign the same accounting entry for each move line that it was reconciled.
        reconciled_lines = res.reconciled_line_ids
        # Join the accounting entries
        self.env['l10n_it.accounting.entry'].join_accounting_entry(reconciled_lines, accounting_entry=None)
        return res
