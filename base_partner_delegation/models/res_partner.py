# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    delegation_ids = fields.One2many(
        string='Delegations',
        comodel_name='res.partner.delegation',
        inverse_name='partner_delegate_id',
        help="It indicates list of delegates",
        copy=False
    )

    def get_partner_delegator(self):
        view_id = self.env.ref('base_partner_delegation.view_res_partner_delegated_tree')
        res_id = self.env['res.partner.delegation'].search([('partner_id.id', '=', self.id)])
        return {
            'name': _("Partner Delegator"),
            'view_mode': 'tree',
            'view_id': view_id.id,
            'view_type': 'form',
            'res_model': 'res.partner.delegation',
            'domain': [('id', 'in', res_id.ids)],
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    @api.constrains('delegation_ids')
    def _check_delegated(self):
        for record in self:
            list_delegated = []
            for delegation in record.delegation_ids:
                list_delegated.append((delegation.partner_id.id, delegation.type))
            if list(set([x for x in list_delegated if list_delegated.count(x) > 1])):
                raise ValidationError(_("It's not possible to continue because the same delegate is delegated twice with the same type."))
            if record.id in record.mapped('delegation_ids.partner_id.id'):
                raise ValidationError(_("It's not possible to continue because one of delegated is the delegator."))
