# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def unlink(self):
        """
            Unlink function has been redefined to be delete account move lines bypassing controls through the context.
            For avoid a infinite loop, the super function has not been called,
            and the move line are deleted via sql query.
        """
        if not self._context.get('check_move_validity_for_delete', False):
            res = super(AccountMoveLine, self).unlink()
            return res
        else:
            moves = self.mapped('move_id')

            # Check the lines are not reconciled (partially or not).
            self._check_reconciliation()

            # Check the lock date.
            moves._check_fiscalyear_lock_date()

            # Check the tax lock date.
            self._check_tax_lock_date()

            #Delete with SQL th move line
            res = self.env.cr.execute('''DELETE FROM account_move_line WHERE id IN %s''', [self._ids])

            return res

