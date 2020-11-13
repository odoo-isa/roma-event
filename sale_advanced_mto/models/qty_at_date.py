# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class QtyAtDate(models.AbstractModel):
    _name = 'qty.at.date'
    _description = 'Abstract model of utils method for qty_at_date widget'

    @api.model
    def get_precision(self, uom_id=None):
        res = {
            'digits': self.env['decimal.precision'].precision_get('Product Unit of Measure')
        }
        if uom_id:
            uom_obj = self.env['uom.uom'].browse(uom_id)
            res['rounding'] = uom_obj.rounding
        return res

    @api.model
    def retrieve_alternative_routing(self, sale_order_line, warehouse_id, product_id, to_date):
        """
        This function retrieve the alternative routing for the warehouse. The only route admitted it's the one that have
        the external id that refere to this module (it was be made by this module).
        :param sale_order_line: the line of the sale order in which the routing should be active
        :param warehouse_id: the warehouse in which find out the alternative routing
        :param product_id: The product of the line
        :param to_date: the scheduled date that is considering by retrieving the available qty
        :return: dictionary of alternative routing
        """
        warehouse = self.env['stock.warehouse'].browse(warehouse_id)
        sale_order_line = self.env['sale.order.line'].browse(sale_order_line)
        sale_order = sale_order_line.order_id
        # from warehouse retrieve the routing that are created in this module
        routing = warehouse.route_ids.filtered(
            lambda r: r.get_external_id()[r.id].split('.')[0] == 'sale_advanced_mto'
        )
        # Create the route structure
        routes = dict()
        for route in routing:
            # Access to the first rule of the route (order by sequence)
            rule = route.rule_ids.sorted(key=lambda r: r.sequence)
            if not rule:
                continue
            # The assumption is that only the first rule (in sequence order) have to be considering as start path.
            # In fact other rule has procure method setting with mts_else_mto while the first rule have procurement
            # method setting with make_to_stock or buy (otherwise cannot be considering as alternative routing).
            # This kind of routes are created automatically from this model.
            rule = rule[0]
            # Check the action of the route (if mto or any other) to retrieve start warehouse
            if rule.action == 'buy':
                warehouse_rule = rule.location_id.get_warehouse()
                routing_action = 'routing_buy'
            elif rule.action == 'pull' and rule.procure_method == 'make_to_stock':
                warehouse_rule = rule.location_src_id.get_warehouse()
                routing_action = 'routing_pull'
            else:
                continue
            # From start warehouse fill the dictionary to return
            rule_dict = routes.setdefault(warehouse_rule.id, {})
            rule_dict.update(warehouse_name=warehouse_rule.name)
            # Save the default route (if exists)
            if route.is_default_route:
                key = routing_action + '_default'
                rule_dict.update({key: route.id})
            # Prepare the routing list
            route_list = rule_dict.setdefault(routing_action, [])
            route_list.append(route.id)
            # Prepare the info about the available qty (today and forecast) if no available
            if 'free_qty' not in rule_dict and routing_action == 'routing_pull':
                # ... retrieve product
                product = self.env['product.product'].browse(product_id)
                if not product:
                    rule_dict.update(today_quantity=0, virtual_available_at_date=0)
                    continue
                # !! Must be invalidate cache !!
                product.invalidate_cache()
                product_qties = product.with_context(
                    warehouse=warehouse_rule.id,
                    to_date=to_date
                ).read([
                    'qty_available',
                    'free_qty',
                    'virtual_available',
                ])
                product_qties = product_qties[0]
                # Find other lines that starting from this warehouse to have the real available qty.
                # If in the sale order line there are other line that replenish product from the same warehouse, the
                # quantity should be decrease considering this quantity.
                order_line_move = sale_order.order_line.is_take_goods_from_warehouse(warehouse_rule, to_date)
                order_line = sale_order.order_line.filtered(
                    lambda l: l.route_id and l.product_id == product and order_line_move[l.id]
                )
                qty_already_in_order = sum(order_line.mapped('product_uom_qty'))
                rule_dict.update(
                    qty_available=max(0, product_qties['qty_available'] - qty_already_in_order),
                    free_qty=max(0, product_qties['free_qty'] - qty_already_in_order),
                    virtual_available=max(0, product_qties['virtual_available'] - qty_already_in_order),
                )
        return routes
