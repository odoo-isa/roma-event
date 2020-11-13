# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        res = super(StockPicking, self).action_done()
        # if Raee module is present in the system, update value of quantity delivered on Sale Order
        installed_module = self.env['ir.module.module'].sudo().search([
            ('name', 'in', ['sale_raee']),
            ('state', '=', 'installed'),
        ])
        if installed_module:
            for record in self:
                for line in record.move_ids_without_package:
                    if line.sale_line_id.link_with_raee:
                        line.sale_line_id.link_with_raee.qty_delivered = line.sale_line_id.link_with_raee.qty_delivered +\
                                                                         line.quantity_done
        return res
