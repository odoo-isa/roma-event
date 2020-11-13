# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import fields, models, api


class AccountAccount(models.Model):
    _inherit = "account.account"

    l10n_it_account_usage = fields.Selection(
        selection_add=[
            ('tax_account', 'Tax Account')
        ]
    )

    @api.model
    def create(self, vals):
        res = super(AccountAccount, self).create(vals)
        if 'l10n_it_account_usage' in vals and vals['l10n_it_account_usage'] == 'tax_account':
            l10n_it_vat_report_obj = self.env['l10n_it.vat.report']
            l10n_it_vat_report_obj.genera_sezioni_da_imposte()
        return res

    def write(self, vals):
        res = super(AccountAccount, self).write(vals)
        if 'l10n_it_account_usage' in vals and vals['l10n_it_account_usage'] == 'tax_account':
            l10n_it_vat_report_obj = self.env['l10n_it.vat.report']
            l10n_it_vat_report_obj.genera_sezioni_da_imposte()
        return res
