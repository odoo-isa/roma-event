# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from . import models
from . import wizard
from . import report
from odoo import api, SUPERUSER_ID


def _setup_account_entry_flag_on_account(cr, registry):
    """
    Setting managed by account entry for debit and credit account
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    pay_rec_account = env['account.account'].search([('user_type_id.type', 'in', ('payable', 'receivable'))])
    pay_rec_account.write({
        'managed_by_accounting_entry': True
    })
