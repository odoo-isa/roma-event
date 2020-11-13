# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_family_ids = fields.One2many(
        string='Supplier Families',
        required=False,
        readonly=False,
        comodel_name='product.supplier.family',
        inverse_name='partner_id',
        help="Indicates the families to which are associated with the supplier",
        copy=False
    )
