# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            group_stock_multi_locations=params.get_param('stock.group_stock_multi_locations', default=True),
            group_stock_adv_location=params.get_param('stock.group_stock_adv_location', default=True),
            group_stock_multi_warehouses=params.get_param('stock.group_stock_multi_warehouses', default=True)
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("stock.group_stock_multi_locations", self.group_stock_multi_locations)
        self.env['ir.config_parameter'].sudo().set_param("stock.group_stock_adv_location", self.group_stock_adv_location)
        self.env['ir.config_parameter'].sudo().set_param("stock.group_stock_multi_warehouses", self.group_stock_multi_warehouses)
