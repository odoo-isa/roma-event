# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount1 = fields.Float(
        string="First Discount %",
        digits='Discount'
    )

    discount2 = fields.Float(
        string="Second Discount %",
        digits='Discount'
    )

    discount3 = fields.Float(
        string="Third Discount %",
        digits='Discount'
    )

    @api.onchange('discount1', 'discount2', 'discount3', 'price_unit')
    def onchange_line_discount(self):
        discount1 = (100 - self.discount1) / 100
        discount2 = (100 - self.discount2) / 100
        discount3 = (100 - self.discount3) / 100
        # Check max discount in product category and compare it with dicount3,
        # if discount3 greater of max discount an error is generate
        if self.product_id.categ_id.set_extra_max_discount:
            max_discount = self.product_id.categ_id.extra_max_discount
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(self.discount3, max_discount, precision_digits=precision) == 1:
                raise ValidationError(_("Warning! The third discount has exceeded the maximum applicable discount. "
                                      "(Maximum discount applicable for this product %s" %(max_discount)))
        tot = 100 - (100 * discount1 * discount2 * discount3)
        self.discount = tot

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        res = super(SaleOrderLine, self)._onchange_discount()
        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy != 'with_discount' and
                self.env.user.has_group('product.group_discount_per_so_line')):
            return
        price, rule = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        rule_id = self.env['product.pricelist.item'].browse(rule)
        if rule_id.compute_price == 'formula':
            self.discount1 = rule_id.discount1
            self.discount2 = rule_id.discount2
            self.discount3 = rule_id.discount3
        return res

    def _prepare_invoice_line(self):
        vals = super(SaleOrderLine, self)._prepare_invoice_line()
        # Adding to line vals value of discount set up on the sale order line.
        vals.update({
            'discount1': self.discount1,
            'discount2': self.discount2,
            'discount3': self.discount3
        })
        return vals


