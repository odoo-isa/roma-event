# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import ValidationError


class StockRule(models.Model):
    _inherit = "stock.rule"

    def unlink(self):
        for record in self:
            route_obj = record.route_id
            external_identifier = self.env['ir.model.data'].search([
                ('res_id', '=', route_obj.id),
                ('model', 'like', 'stock.location.route')
            ])
            if external_identifier:
                raise ValidationError(_(
                    "It's not possible delete this Rule cause is linked to a Route created by warehouse's configuration"
                ))
        return super(StockRule, self).unlink()
