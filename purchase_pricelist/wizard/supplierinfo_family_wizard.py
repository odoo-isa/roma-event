# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from logging import getLogger
_logger = getLogger(__name__)


class SupplierinfoFamilyWizard(models.TransientModel):
    _name = 'supplierinfo.family.wizard'
    _description = 'Wizard: Supplierinfo Family'

    name = fields.Char(
        string='Name'
    )
    profit = fields.Float(
        string='Percentage Profit (%)',
        required=False,
        readonly=False,
        default=0.0,
        digits='Product Price'
    )
    discount_ids = fields.Many2many(
        string='Discounts',
        required=False,
        readonly=False,
        comodel_name='supplierinfo.discount.wizard',
        relation='supplierinfo_family_wizard_supplierinfo_discount_rel',
        column1='supplierinfo_family_wizard_id',
        column2='supplierinfo_discount_wizard_id',
        copy=False
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        required=False,
        readonly=False,
        comodel_name='res.partner'
    )
    calculate_discounts = fields.Html(
        string="Calculate discounts",
        compute='_compute_calculate_discounts'
    )

    @api.depends('discount_ids', 'discount_ids.value')
    def _compute_calculate_discounts(self):
        for record in self:
            list_complete_discounts = []
            discounts = record.discount_ids.sorted('sequence')
            for discount in discounts:
                if discount.label:
                    complete_discount = str(discount.value) + ' (' + discount.label + ') '
                else:
                    complete_discount = str(discount.value)
                list_complete_discounts.append(complete_discount)
            complete_discount = ', '.join(list_complete_discounts)
            record.calculate_discounts = complete_discount
