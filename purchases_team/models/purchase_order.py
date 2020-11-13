# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _calculate_edit_user_id(self):
        self.ensure_one()
        self.edit_user_id = False
        if self.env.is_admin() or self.user_has_groups('purchases_team.group_purchase_buyer'):
            self.edit_user_id = True

    edit_user_id = fields.Boolean(
        string='Edit User',
        compute='_calculate_edit_user_id',
        help="Field that allows to make user_id's field editable only for administrator or who belong "
             "to the Users group: all documents"
    )

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.user_id = False
        else:
            purchase_user_id = self.partner_id.purchase_user_id.id if self.partner_id.purchase_user_id else self.env.uid
            self.user_id = purchase_user_id
        res = super(PurchaseOrder, self).onchange_partner_id()
        return res


