# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProductSupplierFamily(models.Model):
    _name = 'product.supplier.family'
    _description = 'Product Supplier Family'

    name = fields.Char(
        string='Name',
        required=True
    )
    discount_ids = fields.One2many(
        string='Discounts',
        required=False,
        readonly=False,
        comodel_name='supplierinfo.discount',
        inverse_name='product_supplier_family_id',
    )
    calculate_family_discounts = fields.Html(
        string="Calculate family discounts",
        compute='_compute_calculate_family_discounts'
    )
    partner_id = fields.Many2one(
        string='Supplier',
        required=False,
        readonly=False,
        comodel_name='res.partner',
        copy=False,
    )
    profit = fields.Float(
        string='Percentage Profit (%)',
        required=False,
        readonly=False,
        default=0.0,
        digits='Product Price'
    )

    @api.depends('discount_ids', 'discount_ids.value')
    def _compute_calculate_family_discounts(self):
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
            record.calculate_family_discounts = complete_discount
