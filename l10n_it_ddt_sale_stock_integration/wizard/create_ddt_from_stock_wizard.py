# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class CreateDdTFromStockWizard(models.TransientModel):
    _inherit = 'create.ddt.from.stock.wizard'

    @api.model
    def default_get(self, fields):
        """
        Inherit method for passing picking if request came from order
        :param fields:
        :return: dictionary of default
        """
        if self.env.context.get('active_model', None) == 'sale.order':
            res = self.env['create.ddt.from.sale.wizard'].default_get(fields)
        else:
            res = super(
                CreateDdTFromStockWizard, self).default_get(fields)
        return res

    def create_ddt(self):
        self.ensure_one()
        if self.env.context.get('active_model', None) == 'sale.order':
            picking = self._get_picking_form_sale_order()
            picking.ensure_one()
            return super(
                CreateDdTFromStockWizard, self.with_context(active_id=picking.id, active_ids=picking.ids)
            ).create_ddt()
        else:
            return super(CreateDdTFromStockWizard, self).create_ddt()

    def _get_picking_form_sale_order(self):
        """
        Retrieve the picking form sale order
        :return: picking object
        """
        # From sale order retrieve the picking
        order = self.env.context.get('active_ids')
        order = self.env['sale.order'].browse(order)
        picking = order.picking_ids.filtered(lambda p: p.can_create_ddt)
        return picking

    def add_picking_to_ddt(self, picking_obj):
        ddt_id = super(CreateDdTFromStockWizard, self).add_picking_to_ddt(picking_obj)
        ddt_id.weight_net += picking_obj.weight_net
        return ddt_id

    def _get_available_ddt(self, picking, payment_term_id, partner_type):
        available_ddt = super(CreateDdTFromStockWizard, self)._get_available_ddt(picking, payment_term_id, partner_type)
        available_ddt = available_ddt.filtered(lambda ddt: ddt.carrier_id == picking.carrier_id)
        return available_ddt
