# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id', 'order_line', 'sale_order_option_ids')
    def _onchange_order_line(self):
        error = self.check_fgas_license()
        if error:
            return {'warning': error}

    @api.onchange('partner_id', 'order_line', 'sale_order_option_ids')
    def _check_order_line(self):
        error = self.check_fgas_license()
        if error:
            raise ValidationError(error.get('message',False))
        return

    def check_fgas_license(self):
        for record in self:
            products = record.order_line.mapped('product_id')
            product_fgas = products.filtered(lambda p: p.contains_gas)
            products_option = record.sale_order_option_ids.mapped('product_id')
            products_option_fgas = products_option.filtered(lambda p: p.contains_gas)
            if product_fgas and not record.partner_id.fgas_license:
                return {
                    'title': _('Warning'),
                    'message': _(
                        "The partner does not have the f-gas license number, therefore he cannot insert gas products.")
                }
            if products_option_fgas and not record.partner_id.fgas_license:
                return {
                    'title': _('Warning'),
                    'message': _(
                        "The partner does not have the f-gas license number, therefore he cannot insert gas option products.")
                }
