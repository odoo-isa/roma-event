# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    res_partner_bank_id = fields.Many2one(
        string='Partner Bank',
        comodel_name='res.partner.bank',
        help='''This field is used to get Partner Bank Account with associated IBAN code''',
        copy=True,
        default=lambda self: self.move_id.partner_bank_id.id if self.account_id == self.partner_id.property_account_receivable_id else False
    )

