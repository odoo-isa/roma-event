# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields

class AccountAccount(models.Model):
    _inherit = 'account.account'

    related_account_type = fields.Selection(
        related='user_type_id.type',
        string="Account type",
        store=True,
        readonly=True,
        copy=False
    )
