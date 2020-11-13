# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_replacement_purchase_domain(self):
        users = self.env.ref('purchase.group_purchase_user', raise_if_not_found=False)
        return [('groups_id', 'in', users.id)] if users else []

    replacement_purchase_user_ids = fields.Many2many(
        string='Replacements Buyers',
        required=False,
        readonly=False,
        comodel_name='res.users',
        relation='user_replacement_purchase_rel',
        column1='partner_id',
        column2='user_replacement_purchase_id',
        help="Allow to insert a substitutes'list to manage PO",
        copy=False,
        domain=_get_replacement_purchase_domain
    )
