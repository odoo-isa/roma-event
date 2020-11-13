# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    ddt_lines_ids = fields.One2many(
        string='DdT linked lines',
        comodel_name='l10n_it.ddt.line',
        inverse_name='stock_move_id',
        help="Linked DdT lines",
        copy=False,
    )

    qty_in_ddt_invoiced = fields.Float(
        string='Qty in DdT already invoiced',
        readonly=True,
        default=0.0,
        digits='Product Unit of Measure',
        help='''Compute system field to have the qty in ddt that has already invoiced''',
        copy=False,
        compute="_get_ddt_invoice_quantity"
    )

    @api.depends('ddt_lines_ids', 'ddt_lines_ids.state')
    def _get_ddt_invoice_quantity(self):
        for line in self:
            # Quantity in DdT
            line.qty_in_ddt = sum(line.ddt_lines_ids.mapped('quantity'))
            # Quantity in DdT already invoiced
            line.qty_in_ddt_invoiced = sum(
                line.ddt_lines_ids.filtered(lambda l: l.state == 'invoiced').mapped('quantity')
            )

    def _get_quantity_to_invoice(self):
        """
        Calculate the quantity to invoice for passed moves. It considering:
         - returned move
         - returned move to refund
        :return: Quantity to invoice
        """
        qty_to_invoice = 0.0
        for record in self:
            # Reverse move are not considering
            if record.origin_returned_move_id:
                continue
            qty_to_invoice += record.quantity_done - sum(record.mapped('ddt_lines_ids.quantity'))
        return qty_to_invoice

    @api.model
    def prepare_ddt_values(self, quantity, partner_type='customer'):
        self.ensure_one()
        if partner_type == 'customer':
            price = self.product_id.lst_price
            tax = self.product_id.taxes_id
        else:
            price = self.product_id.standard_price
            tax = self.product_id.supplier_taxes_id
        vals = {
            'product_id': self.product_id.id,
            'uom_id': self.product_id.uom_id.id,
            'description': self.product_id.name,
            'quantity': quantity,
            'price_unit': price,
            'ddt_line_tax_ids': [(6, 0, tax.ids)],
            'stock_move_id': self.id,
        }
        return vals