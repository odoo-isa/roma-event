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
    _inherit = "sale.order"

    is_waste_cost_line = fields.Boolean(
        string='Waste cost line',
        compute="_get_waste_cost",
        store=True,
        default=False,
        help="It's useful to compute if in order there is an order line waste applicable",
        copy=True
    )

    @api.depends('order_line')
    def _get_waste_cost(self):
        for record in self:
            len_waste_cost_line = len(self.env['sale.order.line'].search([('order_id', '=', record.id), ('is_waste_cost', '=', True)]))
            if len_waste_cost_line > 0:
                record.is_waste_cost_line = True
            else:
                record.is_waste_cost_line = False

    def compute_waste_cost(self):
        for record in self:
            product_template_id = record.company_id.waste_cost_id.product_tmpl_id
            record._remove_waste_cost()
            for line in record.order_line:
                if line.product_template_id.is_applicable_waste_cost and line.product_template_id.waste_cost_amount > 0:
                    record._add_waste_cost(product_template_id, line)

    def _remove_waste_cost(self):
        self.env['sale.order.line'].search([('order_id', '=', self.id), ('is_waste_cost', '=', True)]).unlink()

    def _add_waste_cost(self, product_template_id, line):
        waste_cost = line.product_template_id.waste_cost_amount
        raee_line = self.env['sale.order.line'].create({
            'order_id': line.order_id.id,
            'customer_lead': self._get_customer_lead(product_template_id),
            'product_template_id': product_template_id.id,
            'product_id': self.company_id.waste_cost_id.id,
            'product_uom_qty': line.product_uom_qty,
            'price_unit': waste_cost,
            'name': _("Waste cost contribution for %s" % (line.name)),
            'product_uom': product_template_id.uom_id.id,
            'is_waste_cost': True,
            'tax_id': [(6, 0, product_template_id.mapped('taxes_id.id'))],
        })
        line.link_with_raee = raee_line