# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import queue
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    stock_quantity_sale_info = fields.One2many(
        string='Sale Quantity Owner',
        help='Information about the product quantity owner reserved for the sale',
        comodel_name='stock.move.quantity.owner.info',
        inverse_name='move_id',
        compute="_get_stock_move_sale_quantity_owner_info",
        store=True
    )

    stock_quantity_sale_info_tree = fields.Html(
        string='Sale Quantity Owner tree',
        help='''Compute field to show the reserved quantity in tree view''',
        compute="_compute_stock_quantity_sale_info_tree",
        store=True,
    )

    @api.depends('move_dest_ids')
    def _get_stock_move_sale_quantity_owner_info(self):
        """
        This method compute for the move if there are reserved quantity for the sale.
        """
        linked_moves = self.get_order_moves('move_dest_ids')  # Retrieve the linked moves
        for move in self:
            move.stock_quantity_sale_info.unlink()
            sale_moves = self.browse([x.id for x in linked_moves[move]])
            sale_moves = sale_moves.filtered(lambda m: m.sale_line_id)  # Get only move with sale res. quant.
            for sale_move in sale_moves:  # Not too much complexity. The move should be in small number
                self.env['stock.move.quantity.owner.info'].create({
                    'move_id': move.id,
                    'doc_reference': f"sale.order,{sale_move.sale_line_id.order_id.id}",
                    'quantity': sale_move.sale_line_id.product_uom_qty
                })

    @api.depends('stock_quantity_sale_info')
    def _compute_stock_quantity_sale_info_tree(self):
        for move in self:
            quant_info = ', '.join([
                f'''<b>{x.doc_reference.name}</b>({x.quantity})''' for x in move.stock_quantity_sale_info
            ])
            move.stock_quantity_sale_info_tree = quant_info

    def get_order_moves(self, field) -> dict:
        """
        This function return dict with this structure:
        { stock.move(): [stock.move(), stock.move(), stock.move()]}
        key = started stock move
        value = list of linked move congruent with required document type
        :params self: Objects of stock.move
        :params field: String could be: move_orig_ids/move_dest_ids
        """
        res = dict()
        for move in self:
            move_list = res.setdefault(move, [])
            tail = queue.Queue()
            tail.put(move)
            while not tail.empty():
                move_obj = tail.get()
                move_list.append(move_obj)
                for link_move in getattr(move_obj, field):
                    if link_move.state == 'cancel':
                        continue
                    tail.put(link_move)  # Load linked move
        return res
