# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, _
from logging import getLogger
_logger = getLogger("Management Warehouses")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    warehouse_dest_id = fields.Many2one(
        string='Warehouse Dest',
        required=False,
        readonly=False,
        comodel_name='stock.warehouse',
        help="",
        copy=False
    )

    def _get_route_by_warehouse_dest(self):
        if not self.warehouse_dest_id or not self.order_id.picking_type_id.warehouse_id:
            return
        warehouse_dest_id = self.warehouse_dest_id.id
        po_warehouse_src_id = self.order_id.picking_type_id.warehouse_id.id
        # Find Route from warehouse_src to warehouse_dest
        route_external_id = "stock_location_route_behalf_" + str(po_warehouse_src_id) + "_" + str(warehouse_dest_id)
        behalf_route_obj = self.env.ref('sale_advanced_mto.' + route_external_id, False)
        if behalf_route_obj:
            if not behalf_route_obj.active:
                # Active Route, rules and picking types
                _logger.info(_("Restore Route: ") + behalf_route_obj.name)
                behalf_route_obj.write({'active': True})
                behalf_route_obj.with_context(active_test=False).rule_ids.write({'active': True})
                behalf_route_obj.rule_ids.with_context(active_test=False).mapped('picking_type_id').write({'active': True})
        return behalf_route_obj

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        route_ids = res[0].get('route_ids', False)
        if route_ids:
            behalf_route_obj = self._get_route_by_warehouse_dest()
            if not behalf_route_obj:
                return res
            route_ids[0][2].append(behalf_route_obj.id)
        return res
