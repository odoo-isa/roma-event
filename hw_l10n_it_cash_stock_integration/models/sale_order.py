# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import queue
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def print_bill(self):
        """
        Check if it is possible to print the cash bill. Check the availability of the goods and look up for
        configuration if it is possible to confirm ship by force the availability.
        :return:
        """
        # Perform this operation with sudo because the banker user should not have permission
        self = self.sudo()
        self.ensure_one()
        # Get the moves linked to the sale order line of the first picking (case are present more than one step)
        # The picking have to be validated in order
        first_pick = self.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done']).sorted(lambda p: p.id)
        if not first_pick:
            return super(SaleOrder, self).print_bill()
        first_pick = first_pick[0]
        moves = self.env['stock.move'].search([
            ('state', 'not in', ('cancel', 'done')),
            ('picking_id', '=', first_pick.id)
        ])
        # If not moves founded means that the sale is a services sales or quantity are already moved
        if not moves:
            return super(SaleOrder, self).print_bill()
        # Check if no lots when needed
        use_lots = any(
            moves.mapped('picking_type_id.use_create_lots') +
            moves.mapped('picking_type_id.use_existing_lots')
        )
        any_product_tracking = any([t != 'none' for t in moves.mapped('product_id.tracking')])
        if use_lots and any_product_tracking:
            raise UserError(_('Some products require lots/serial numbers.'))
        # Check for picking state
        try:
            first_pick.action_assign()
        except UserError:
            # Picking is already assign
            pass
        # Check move state
        moves_to_assign = any([state != 'assigned' for state in moves.mapped('state')])
        if moves_to_assign and not self.company_id.cash_register_force_reserve:
            raise UserError(_("There are not available quantity. Unable to proceed."))
        return super(SaleOrder, self).print_bill()

    def transfer_sale_picking(self):
        self = self.sudo()
        # Check for picking state
        pickings = self.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done']).sorted(lambda p: p.id)
        # Set quantity done
        for picking in pickings:
            # Have to assign confirmed quantity
            for move in picking.move_lines:
                move.quantity_done = move.product_uom_qty
            res = picking.button_validate()
            # Check for immediate transfer (this options should be never occur cause of quantity reservation)
            if type(res) == dict and res.get('res_model', None) == 'stock.immediate.transfer':
                immediate_transfer = self.env['stock.immediate.transfer'].browse(res['res_id'])
                immediate_transfer.process()
            elif type(res) == dict and res.get('res_model', None) == 'stock.backorder.confirmation':
                backorder = self.env['stock.backorder.confirmation'].browse(res['res_id'])
                backorder.process()
            else:
                # All quantity are done
                pass
