# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError
from collections import defaultdict
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    display_cancelled_route_widget = fields.Boolean(
        string='Display cancelled route widget',
        help='''System field to check if display cancelled route.''',
        compute='_compute_display_cancelled_route_widget'
    )

    @api.depends('route_id', 'state')
    def _compute_display_cancelled_route_widget(self):
        """
        This function is used to determinate if the widget should be visible in the sale order line view.
        :return: void
        """
        for line in self:
            line.display_cancelled_route_widget = False
            if not line._origin:
                continue
            if line.state in ('done', 'cancelled'):
                continue
            if not line.route_id:
                continue
            if not line.route_id.is_sale_mto_routing:
                continue
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_is_zero(line.product_uom_qty, precision_digits=precision):
                continue
            line.display_cancelled_route_widget = True

    def _compute_qty_to_deliver(self):
        """Don't show inventory widget for order lines with route."""
        super(SaleOrderLine, self)._compute_qty_to_deliver()
        self.filtered(lambda sol: sol.route_id).write({
            'display_qty_widget': False
        })

    def dispatch_lines_by_routing(self, happy_path):
        """
        Split and dispatch sale order line (self) based to happy path dictionary.
        The happy path has two key: pull_rule and buy_rule.
        Pull --> it is used for pull quantity from another warehouse instead of the default one.
        Buy --> it is used for make to order.
        Each key has the quantity and the route to apply.
        Based to the quantity the default sale.order.line (self) will be split and will update the product_uom_qty.
        New sale order line it will be created and will be set with the correct route_id.
        This function will be performed by the superuser because the current user may not have the right authorization
        (may not manage the route id)
        :param happy_path:
        :return: boolean
        """
        # If not happy path nothing to do
        if not(any(happy_path[x] for x in happy_path)):
            return True
        # if line has route_id it means that this is a route changed
        is_route_changes = False
        if self.route_id:
            self.cancel_moves()
            is_route_changes = True
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # Check if total dispatch quantity is greater than required quantity
        qty_to_dispatch = sum([float_round(x[0], precision_digits=precision) for x in happy_path['pull_rule'].values()])
        qty_to_dispatch += sum([float_round(x[0], precision_digits=precision) for x in happy_path['buy_rule'].values()])
        compare = float_compare(qty_to_dispatch, self.product_uom_qty, precision_digits=precision)
        if compare > 1:
            raise UserError(_(
                "Procured quantity cannot be greater than ordered quantity"
            ))
        # During routing change, the procured quantity must be equal to the required quantity
        if is_route_changes and compare != 0:
            raise UserError(_(
                "Case of change warehouse routing, the procured quantity must be equal to the required quantity."
            ))
        # Create the pull rule lines
        self._create_dispatch_line(happy_path['pull_rule'].values(), precision, is_route_changes)
        # Create the buy rule lines
        self._create_dispatch_line(happy_path['buy_rule'].values(), precision, is_route_changes)
        # Update the quantity of the original sale order line
        new_qty = self.product_uom_qty - qty_to_dispatch
        if float_is_zero(new_qty, precision_digits=precision) and not is_route_changes:
            self.sudo().unlink()
        else:
            self.sudo().product_uom_qty = new_qty
        return True

    def _create_dispatch_line(self, happy_path_data, precision, is_route_changes):
        """
        Copy the original line to create dispatch line.
        :param happy_path_data: tuple of quantity and route
        :param precision: precision used for rounding and compare
        :return: True
        """
        for qty, route_id in happy_path_data:
            qty = float_round(qty, precision_digits=precision)
            if float_compare(qty, 0, precision_digits=precision) in (-1, 0):
                raise UserError(_("Quantity cannot be zero or lower then it."))
            if not route_id:
                raise UserError(_("Must be select routing."))
            # Search if, in the sale order, there are already line with same product and same route
            order = self.order_id
            equivalent_line = order.order_line.filtered(
                lambda l: l.route_id.id == route_id and l.product_id == self.product_id
            )
            if equivalent_line and not is_route_changes:
                equivalent_line[0].product_uom_qty += qty
            else:
                self.sudo().copy({
                    'order_id': self.order_id.id,
                    'product_uom_qty': qty,
                    'route_id': route_id
                })
        return True

    def revert_route_to_default_warehouse(self):
        """
        This function erase the route_id field to revert to default.
        Search for existing line for the same product that doesn't have route setting.
        Considering the state of the sale order: if not in sale state we don't touch the stock.move.
        :return: void
        """
        # Check for existing picking
        if self.order_id.state in ('sale', 'done'):
            # Cancel move
            self.cancel_moves()
            # Copy the line and set old with zero
            new_line = self.copy({
                'order_id': self.order_id.id,
                'route_id': False,
                'sequence': 0  # have to be push to the top
            })
            self.product_uom_qty = 0
        else:
            self.route_id = None
            # Search for a line to join
            equivalent_line = self.search([
                ('route_id', '=', False),
                ('order_id', '=', self.order_id.id),
                ('product_id', '=', self.product_id.id),
                ('id', '!=', self.id)
            ], limit=1)
            if equivalent_line:
                equivalent_line.product_uom_qty += self.product_uom_qty
                self.unlink()
        return True

    def cancel_moves(self):
        """
        This function is used for cancel the move line linked to the sale order line. The move line should be cancel if
        in the related sale order line it was changed or cancelled the route. This function also log a message in the
        purchase order (as Warning) if any line of the sale order has generated it.
        :return:
        """
        move_to_cancel = self.move_ids
        # Have to cancel linked moves
        move_origin = move_to_cancel.mapped('move_orig_ids')
        while move_origin:
            move_to_cancel += move_origin
            move_origin = move_origin.mapped('move_orig_ids')
        move_to_cancel._action_cancel()
        # Check for Purchase order
        purchase_line_warning = move_to_cancel.sudo().mapped('created_purchase_line_id')
        if purchase_line_warning:
            self.sudo()._log_warning_on_po(purchase_line_warning)
        # Check for picking that has only cancel moved
        pick_to_unlink = move_to_cancel.mapped('picking_id').filtered(
            lambda p: all([move.state == 'cancelled' for move in p.move_lines])
        )
        if pick_to_unlink:
            pick_to_unlink.action_cancel()
            pick_to_unlink.unlink()
        return True

    def _log_warning_on_po(self, purchase_line_warning):
        """
        This function is used to log the error in the purchase order in case in the sale order (that have generated it)
        change the route or cancel the route for the specific line of product.
        :param purchase_line_warning: th purchase order line in which set the warning log
        :return: void
        """
        for p_order in purchase_line_warning.mapped('order_id'):
            # Get the line in warning
            p_lines = purchase_line_warning.filtered(lambda l: l.order_id == p_order)
            products_list = ["<li>%s</li>" % line.product_id.name for line in p_lines]
            message = _(
                '''Please check this products in sale order (%(order)s) because for them it was changed the route:<br/>
                <ul>%(products)s</ul>''' % {
                    'order': p_order.origin,
                    'products': ''.join(products_list)
                }
            )
            p_order.activity_schedule('mail.mail_activity_data_warning', note=message, user_id=self.env.user.id)

    def is_take_goods_from_warehouse(self, warehouse, to_date):
        """
        Check if the route is a pull rule type (no MTO) and the path take goods from specific warehouse.
        How to check it:
        - The route must to be specified in the sale order line
        - The route have to involve the goods in the warehouse. The route must have a rule with this requirements that
          should be met:
            1) The rule should be have the specific warehouse as location_src_id
            2) The rule should be have an action setting with pull or pull_push
            3) The procure method should be set with:
                i)  make_to_stock
                ii) mts_else_mto but only if current_qty_at_warehouse is greater or equal than the required qty on the
                    sale order line
        :param warehouse: warehouse to check if it's goods are taken.
        :param to_date: date of the order
        :return: dictionary -> for each line: True if the route take goods from specific warehouse, false otherwise.
        """
        res = defaultdict(lambda: False)
        # Retrieve the available quantity of products for the warehouse
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        product_qties = self.product_id.with_context(
            warehouse=warehouse.id,
            to_date=to_date
        ).read(['qty_available'])
        product_quantities = {d['id']: d['qty_available'] for d in product_qties}
        for order_line in self.sorted(key=lambda l: l.sequence):
            if not order_line.route_id:
                continue
            # Retrieve the location from the warehouse
            location = warehouse.lot_stock_id
            # From the route get the rule that have action setting with pull and location_src_id with warehouse
            # specified in arguments
            route = order_line.route_id
            rules = route.rule_ids.filtered(
                lambda r: r.location_src_id == location and r.action in ('pull', 'pull_push')
            )
            if not rules:
                continue
            allowed_procure_method = ['make_to_stock']
            # As allowed procure method add also mts_else_mto (make to stock or trigger another rule) but only if there
            # are quantity of good able to met the required quantity of the order line (considering other lines)
            available_today = product_quantities[order_line.product_id.id]
            if float_compare(order_line.product_uom_qty, available_today, precision_digits=precision) in (0, -1):
                allowed_procure_method.append('mts_else_mto')
            # Search for the rule
            rules = rules.filtered(lambda r: r.procure_method in allowed_procure_method)
            if not rules:
                continue
            # Update the available quantity with the quantity that should be pick from the location
            product_quantities[order_line.product_id.id] = available_today - order_line.product_uom_qty
            res[order_line.id] = True
        return res
