# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, _
from logging import getLogger

_logger = getLogger(__name__)


class SupplierinfoDiscount(models.Model):
    _name = 'supplierinfo.discount'
    _description = 'Supplierinfo Discount'

    value = fields.Float(
        string='Value',
        required=False,
        readonly=False,
        digits='Product Price'
    )
    label = fields.Char(
        string='Label',
        copy=False
    )
    sequence = fields.Integer(
        string='Sequence'
    )
    product_supplier_family_id = fields.Many2one(
        string='Product Supplier Family',
        required=False,
        readonly=False,
        comodel_name='product.supplier.family'
    )
