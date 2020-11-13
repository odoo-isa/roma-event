# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResPartnerDelegation(models.Model):
    _name = "res.partner.delegation"
    _description = "Model to allow delegations from partner"

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        help="Partner who is delegated",
        copy=False
    )

    type = fields.Selection(
        string='Type',
        default='purchase_goods',
        selection=[('purchase_goods', 'Purchase and Pick up Goods'), ('pick_up_goods', 'Pick Up Goods'), ('give_back_goods', 'Give Back Goods')],
        help="Type of delegation",
        copy=False
    )

    delegation_document = fields.Binary(
        string='Delegation Document',
        help="Document with delegation in",
        copy=False
    )

    active_delegation = fields.Boolean(
        string='Active',
        help="It indicates if delegation is valid or not",
        default=True,
        copy=False
    )

    partner_delegate_id = fields.Many2one(
        string='Delegator',
        comodel_name='res.partner',
        help="Delegator",
        copy=False
    )

    delegation_file_name = fields.Char(
        string='Delegation File Name',
        compute="_get_delegation_file_name",
        help="Customize name of download pdf delegation",
        copy=False
    )

    note = fields.Text(
        string='Note',
        help="It is useful to write some note about delegation",
        copy=False
    )

    def _get_delegation_file_name(self):
        self.ensure_one()
        filename = "Delegation model %s" % self.partner_delegate_id.name
        self.delegation_file_name = filename

    def print_delegation(self):
        data = {
            'res_partner': self.partner_delegate_id.id
        }
        return self.env.ref('base_partner_delegation.partner_delegation').report_action(self, data=data)
