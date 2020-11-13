# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    stock_quantity_sale_info = fields.One2many(
        string='Sale Quantity Owner',
        help='Information about the product quantity owner reserved for the sale',
        comodel_name='stock.move.quantity.owner.info',
        inverse_name='purchase_line_id',
        compute="_get_stock_move_sale_quantity_owner_info",
        store=True
    )
    stock_quantity_sale_info_tree = fields.Html(
        string='Sale Quantity Owner tree',
        help='''Compute field to show the reserved quantity in tree view''',
        compute="_compute_stock_quantity_sale_info_tree",
        store=True
    )

    @api.depends('move_dest_ids')
    def _get_stock_move_sale_quantity_owner_info(self):
        """
        This method compute for the move if there are reserved quantity for the sale.
        """
        for record in self:
            record.stock_quantity_sale_info.unlink()
            move_dest_ids = record.move_dest_ids
            linked_moves = move_dest_ids.get_order_moves('move_dest_ids')  # Retrieve the linked moves
            for move in move_dest_ids:
                sale_moves = record.env['stock.move'].browse([x.id for x in linked_moves[move]])
                sale_moves = sale_moves.filtered(lambda m: m.sale_line_id)  # Get only move with sale res. quant.
                for sale_move in sale_moves:  # Not too much complexity. The move should be in small number
                    record.env['stock.move.quantity.owner.info'].create({
                        'doc_reference': f"sale.order,{sale_move.sale_line_id.order_id.id}",
                        'quantity': sale_move.sale_line_id.product_uom_qty,
                        'purchase_line_id': record.id
                    })

    @api.depends('stock_quantity_sale_info')
    def _compute_stock_quantity_sale_info_tree(self):
        for record in self:
            quant_info = ', '.join([
                f'''<b>{x.doc_reference.name}</b>({x.quantity})''' for x in record.stock_quantity_sale_info
            ])
            record.stock_quantity_sale_info_tree = quant_info
