# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        res = super(StockMove, self)._assign_picking()
        picking_id = self.mapped('picking_id')
        for move in self:
            move_orig_ids = move.get_order_moves('move_orig_ids')
            origin_move_obj = move_orig_ids[move][-1]
            move_dest_ids = move.get_order_moves('move_dest_ids')
            dest_move_obj = move_dest_ids[move][-1]
            new_origin = origin_move_obj.location_id.display_name + ' - ' + dest_move_obj.location_dest_id.display_name
        old_picking_origin = picking_id.origin
        if old_picking_origin:
            new_origin_picking = old_picking_origin + ': ' + new_origin
        else:
            new_origin_picking = new_origin
        picking_id.write({'origin': new_origin_picking})
        return res
