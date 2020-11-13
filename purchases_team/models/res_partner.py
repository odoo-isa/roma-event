# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _calculate_edit_purchase_user_id(self):
        self.ensure_one()
        self.edit_purchase_user_id = False
        if self.env.is_admin() or self.user_has_groups('purchases_team.group_purchase_buyer'):
            self.edit_purchase_user_id = True

    edit_purchase_user_id = fields.Boolean(
        string='Edit Purchase User',
        compute='_calculate_edit_purchase_user_id',
        help="Field that allows to make purchase_user_id's field editable only for administrator or who belong "
             "to the Users group: all documents"
    )
    purchase_user_id = fields.Many2one(
        string='Purchase User',
        required=False,
        readonly=False,
        comodel_name='res.users',
        ondelete='cascade',
        help="Indicates user associated with the supplier for PO",
        copy=False,
    )


