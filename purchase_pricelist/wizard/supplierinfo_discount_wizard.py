# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, _
from logging import getLogger
_logger = getLogger(__name__)


class SupplierinfoDiscountWizard(models.TransientModel):
    _name = 'supplierinfo.discount.wizard'
    _description = 'Wizard: Supplierinfo Discount'

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

