# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class L10nItDdt(models.Model):
    _inherit = "l10n_it.ddt"

    @api.model
    def create(self, vals):
        # eredito la create del modello dei ddt per valorizzare il buono d'ordine del rispettivo ordine, se c'è
        if self._context.get('active_model', False) == 'stock.picking':
            stock_picking_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
            sale_order_id = stock_picking_id.group_id.sale_id
            vals['client_purchase_order_ids'] = [(6, 0, sale_order_id.mapped('client_purchase_order_ids.id'))]
        return super(L10nItDdt, self).create(vals)
    
    def write(self, vals):
        for record in self:
            if record._context.get('active_model', False) == 'stock.picking':
                stock_picking_id = self.env[record._context.get('active_model')].browse(record._context.get('active_id'))
                sale_order_id = stock_picking_id.group_id.sale_id
                vals['client_purchase_order_ids'] = []
                for client_purchase_order_id in sale_order_id.client_purchase_order_ids:
                    vals['client_purchase_order_ids'].append((4, client_purchase_order_id.id, 0))
        return super(L10nItDdt, self).write(vals)
