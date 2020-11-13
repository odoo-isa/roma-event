# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends(
        'order_line.qty_in_ddt',
        'order_line.qty_delivered',
        'order_line.qty_in_ddt_invoiced',
        'order_line.qty_invoiced',
        'picking_ids',
        'picking_ids.state',
        'picking_ids.ddt_ids',
    )
    def _get_can_create_ddt(self):
        """
        Override method to check the possibility to create DdT form sale order.
        Only if:
         * Exist ONLY one picking that can generate DdT
        :return: bool
        """
        for order in self:
            pickings = order.picking_ids.filtered(lambda p: p.can_create_ddt)
            order.can_create_ddt = False
            if len(pickings) == 1:
                order.can_create_ddt = True
