# -*- coding: utf-8 -*-

from odoo import models, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    _sql_constraints = [
        ('default_code', 'UNIQUE(default_code)', "Default code must be unique ! Please choose another one.")
    ]

    def write(self, vals):
        # Inherits this method because if setting Default Code to False,
        # must be replaced in one variant
        for record in self:
            if 'default_code' in vals:
                if not vals['default_code'] and len(record.product_variant_ids) == 1:
                    record.product_variant_ids.default_code = False
            super(ProductTemplate, self).write(vals)
        return True

    def _set_default_code(self):
        # Override this method because when only a variant is set, template's internal reference is set to False: so
        # enter in product write method and recalculates the internal reference from Products Default Code sequence
        for template in self:
            if len(template.product_variant_ids) == 1:
                if template.product_variant_ids.default_code and not template.default_code:
                    template.default_code = template.product_variant_ids.default_code
                # it's the basic logic
                else:
                    template.product_variant_ids.default_code = template.default_code

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        this = self
        # When is selected product on search. the inactive ones are also filtered
        if name:
            this = this.with_context(active_test=False)
        return super(ProductTemplate, this)._name_search(
            name, args, operator, limit, name_get_uid
        )
