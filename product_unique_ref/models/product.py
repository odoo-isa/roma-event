# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [
        ('default_code', 'UNIQUE(default_code)', "Default code must be unique ! Please choose another one.")
    ]

    def set_default_code_product(self):
        # Retrieve sequence about product's internal reference
        default_code_sequence = self.env.ref('product_unique_ref.seq_products_default_code', False)
        ref = default_code_sequence.next_by_id()
        return ref

    @api.model
    def create(self, vals):
        if 'default_code' not in vals or not vals['default_code']:
            ref = self.set_default_code_product()
            vals['default_code'] = ref
        return super(ProductProduct, self).create(vals)

    def write(self, vals):
        for record in self:
            if 'active' in vals and vals.get('active') and not record.default_code:
                ref = self.set_default_code_product()
                vals['default_code'] = ref
            super(ProductProduct, record).write(vals)
        return True

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        product_ids = []
        if name:
            product_ids = self.search([('barcode', '=', name)] + args)
        if not product_ids and name:
            product_ids = self.env['product.packaging'].search([('barcode', '=', name)])
            product_ids = product_ids.mapped('product_id')
        if not product_ids and name:
            domain = ['|', '|', ('name', operator, name), ('default_code', operator, name),
                      ('seller_ids.product_code', operator, name)]
            product_ids = self.env['product.product'].search(domain + args)
        if product_ids:
            return models.lazy_name_get(self.browse(product_ids.ids).with_user(name_get_uid))
        return super(ProductProduct, self)._name_search(name, args, operator, limit, name_get_uid)
