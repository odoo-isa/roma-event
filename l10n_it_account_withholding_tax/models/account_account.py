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
        selection_add=[
            ('withholding_tax', 'withholding tax')
        ]
    )
