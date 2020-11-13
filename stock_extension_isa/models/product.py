# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_supplier_id = fields.Many2one(
        string='Default Supplier',
        required=False,
        readonly=False,
        comodel_name='res.partner',
        help="Indicates the usual supplier"
    )

    @api.onchange('seller_ids')
    def onchange_seller_ids(self):
        suppliers_list = []
        all_suppliers = self.seller_ids.mapped('name')
        if all_suppliers:
            suppliers_list.extend(all_suppliers.ids)
            return {
                'domain': {
                    'default_supplier_id': [('id', 'in', suppliers_list)]
                }
            }
        else:
            self.default_supplier_id = None

