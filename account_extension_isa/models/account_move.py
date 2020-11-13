# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _


class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_bank_id = fields.Many2one(
        string='Partner Bank',
        required=False,
        readonly=False,
        comodel_name='res.partner.bank',
        ondelete='restrict',
        help='This field is set to the default bank account associated with the Customer/Supplier. It can be further '
             'modified by the user, choosing from the Customer/Supplier bank accounts',
        copy=False,
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_ext_isa(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if not res:
            res = {}
        if self.partner_id and (self.partner_id.bank_ids or(self.partner_id.type == 'invoice' and self.partner_id.parent_id and self.partner_id.parent_id.bank_ids)):
            bank_list = []
            if self.partner_id.bank_ids:
                bank_list += self.partner_id.bank_ids[0].ids
                self.partner_bank_id = self.partner_id.bank_ids[0].id

            bank_ids = self.partner_id.bank_ids.filtered(lambda l: l.default)
            if bank_ids:
                self.partner_bank_id = bank_ids[0].id
                bank_list += bank_ids.ids

            if self.partner_id.type == 'invoice' and self.partner_id.parent_id and self.partner_id.parent_id.bank_ids:
                bank_list += self.partner_id.parent_id.bank_ids.ids
                parent_bank_id = self.partner_id.parent_id.bank_ids.filtered(lambda b: b.default)
                if parent_bank_id:
                    self.partner_bank_id = parent_bank_id[0].id
                else:
                    self.partner_bank_id = self.partner_id.parent_id.bank_ids[0].id

            domain = [('id', 'in', bank_list)]
            res.setdefault('domain', {})['partner_bank_id'] = domain
        if not self.partner_id or \
                (self.partner_id and not self.partner_id.bank_ids and not self.partner_id.parent_id) or \
                ( self.partner_id and self.type == 'invoice' and self.partner_id.parent_id and not self.partner_id.parent_id.bank_ids):
            self.partner_bank_id = None
            res.setdefault('domain', {})['partner_bank_id'] = [('id', 'in', [])]
        return res

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        bank_ids = res.partner_id.bank_ids
        if bank_ids:
            default_bank = bank_ids.filtered(lambda l: l.default)
            if default_bank:
                res.partner_bank_id = default_bank.id
        return res

    @api.onchange('partner_bank_id')
    def onchange_partner_bank(self):
        for line in self.line_ids:
            if line.account_id == line.partner_id.property_account_receivable_id and not line.res_partner_bank_id:
                line.res_partner_bank_id = self.partner_bank_id

