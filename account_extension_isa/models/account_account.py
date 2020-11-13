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
    _inherit = 'account.account'

    l10n_it_account_usage = fields.Selection(
        string='Usage',
        default='standard',
        selection=[('standard', 'Standard')],
        help="That indicate the usage of this account",
        copy=False,
    )
