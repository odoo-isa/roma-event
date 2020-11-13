# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    ddt_lines_ids = fields.One2many(
        string='DdT linked lines',
        comodel_name='l10n_it.ddt.line',
        inverse_name='sale_order_line_id',
        help="Linked DdT lines",
        copy=False,
    )

    qty_in_ddt = fields.Float(
        string='Qty in Delivery Note',
        readonly=True,
        digits='Product Unit of Measure',
        compute="_get_in_ddt_qty",
        store=True,
        help="Quantity added in Delivery Note",
        copy=False,
        default=0.0,
        compute_sudo=True
    )

    qty_in_ddt_invoiced = fields.Float(
        string='Qty in DdT already invoiced',
        readonly=True,
        default=0.0,
        digits='Product Unit of Measure',
        help='''Compute system field to have the qty in ddt that has already invoiced''',
        copy=False,
        compute="_get_in_ddt_qty",
        compute_sudo=True
    )

    @api.depends('ddt_lines_ids', 'ddt_lines_ids.state')
    def _get_in_ddt_qty(self):
        for line in self:
            # Quantity in DdT
            line.qty_in_ddt = sum(line.ddt_lines_ids.mapped('quantity'))
            # Quantity in DdT already invoiced
            line.qty_in_ddt_invoiced = sum(
                line.ddt_lines_ids.filtered(lambda l: l.state == 'invoiced').mapped('quantity')
            )

    def get_quantity_available_for_ddt(self):
        """
        This method return True if an order can create a DdT based to this formula:
        quantity_available_for_ddt = qty_delivered - qty_in_ddt - (qty_invoiced - qty_in_ddt_invoiced)
        :return: The quantity already available for DdT
        """
        qty_available_for_ddt = self.qty_delivered - self.qty_in_ddt - (self.qty_invoiced - self.qty_in_ddt_invoiced)
        return qty_available_for_ddt

    @api.depends(
        'qty_invoiced',
        'qty_delivered',
        'product_uom_qty',
        'order_id.state',
        'qty_in_ddt',
        'qty_in_ddt_invoiced'
    )
    def _get_to_invoice_qty(self):
        """
        Inherited method to modify the quantity to invoice related to sale.order.line.
        This field is used in the method that create the invoice start from sale.order.
        The quantity to invoice shouldn't considering the quantity in DdT because these one
        have to be invoiced by deferred invoice.
        The quantity of sale.order to be invoiced (if invoice_policy is no equal to order) must be:
        quantity to invoice = delivery_quantity - invoiced quantity - quantity in ddt not already invoiced.
        If the quantity in DdT is already invoiced, doesn't have to be considering because is already considering in
        the invoiced quantity.
        the formula is:
        qty_to_invoice = delivery_quantity - invoiced quantity - (quantity in ddt - quantity in ddt invoiced)
        """
        super(SaleOrderLine, self)._get_to_invoice_qty()
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                line.qty_to_invoice -= (line.qty_in_ddt - line.qty_in_ddt_invoiced)
                if line.qty_to_invoice < 0 and not line.is_downpayment:
                    line.qty_to_invoice = 0

    @api.model
    def prepare_ddt_values(self, quantity):
        self.ensure_one()
        vals = {
            'product_id': self.product_id.id,
            'uom_id': self.product_id.uom_id.id,
            'description': self.name,
            'quantity': quantity,
            'ddt_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'price_unit': self.price_unit,
            'sale_order_line_id': self.id,
            'discount': self.discount
        }
        return vals
