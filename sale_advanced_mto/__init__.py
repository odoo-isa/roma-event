# -*- coding: utf-8 -*-

from . import models

from odoo import api, SUPERUSER_ID


def _update_warehouse_transit_location_and_buy_for_sold_route(cr, registry):
    """
    This hook is used to add transit location on every warehouse.
    It's necessary if some warehouses were already created.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    warehouses = env["stock.warehouse"].search([])
    for warehouse in warehouses:
        # Update or Create transit location for this warehouse
        warehouse._update_transit_location()
        # Update or Create Receipt Sale Type
        warehouse._create_receipt_picking_type()
        # Update or Create Shipment Sale Type
        warehouse._create_shipment_picking_type()
