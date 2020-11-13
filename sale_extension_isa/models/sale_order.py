# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        # Search a valid product by barcode
        quantity = 1
        product = self.env['product.product'].search([('barcode', '=', barcode)])
        # Search for packaging ean
        if not product:
            product = self.env['product.packaging'].search([('barcode', '=', barcode)], limit=1)
            quantity = product.qty if product else 0
            product = product.mapped('product_id')
        if not product:
            return {
                'warning': {
                    'title': _("No product founded"),
                    'message': _("It is no possible find a product with %s barcode" % barcode)
                }
            }
        if len(product) > 1:
            return {
                'warning': {
                    'title': _("Too many products"),
                    'message': _("It was find more than one product with %s barcode" % barcode)
                }
            }
        # Search for existing sale order line
        so_line = self.order_line.filtered(lambda l: l.product_id == product)
        if so_line:
            so_line = so_line[0]
            so_line.update({'product_uom_qty': so_line.product_uom_qty+quantity})
            return
        # Otherwise create new line
        so_line = self.env['sale.order.line'].new({
            'name': 'ciao',
            'product_id': product,
            'product_uom_qty': 1,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'price_unit': product.list_price,
            'order_id': self.id
        })
        so_line.product_id_change()
        so_line._compute_tax_id()
