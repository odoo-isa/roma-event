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

    can_create_ddt = fields.Boolean(
        string='Can Create DDT',
        compute="_get_can_create_ddt",
        store=True,
        help="Compute system field used for show or hide the create ddt button",
        copy=False,
        default=False
    )

    ddt_ids = fields.Many2many(
        string='DdT',
        required=False,
        comodel_name='l10n_it.ddt',
        help="Ddt that are linked to specific order",
        copy=False,
        compute="_get_ddt",
        store=True,
    )

    ddt_count = fields.Integer(
        string='# DdT',
        readonly=True,
        default=0,
        help="Number of DdT linked to order.",
        copy=False,
        compute="_get_ddt",
        store=True
    )

    qty_to_invoice_from_ddt = fields.Float(
        string='Qty to invoice from DdT',
        default=0.0,
        digits='Product Unit of Measure',
        compute="_get_qty_to_invoice_from_ddt",
        store=True
    )

    # FUNCTION TO EVALUATE COMPUTE FIELDS

    @api.depends(
        'order_line.qty_in_ddt',
        'order_line.qty_delivered',
        'order_line.qty_in_ddt_invoiced',
        'order_line.qty_invoiced'
    )
    def _get_can_create_ddt(self):
        """
        This method check if sale order can generate ddt.
        An order can generate DdT if there is quantity to add in ddt.
        :return: bool
        """
        for order in self:
            quantity_available_for_ddt = 0
            for line in order.order_line:
                quantity_available_for_ddt += line.get_quantity_available_for_ddt()
            order.can_create_ddt = quantity_available_for_ddt > 0

    @api.depends('order_line.ddt_lines_ids')
    def _get_ddt(self):
        for order in self:
            order.ddt_ids = order.mapped('order_line.ddt_lines_ids.l10n_it_ddt_id.id')
            order.ddt_count = len(order.ddt_ids)

    @api.depends(
        'order_line.ddt_lines_ids',
        'order_line.ddt_lines_ids.state',
        'order_line.ddt_lines_ids.l10n_it_ddt_id.invoice_option'
    )
    def _get_qty_to_invoice_from_ddt(self):
        for order in self:
            ddt_to_invoice = order.order_line.mapped('ddt_lines_ids.l10n_it_ddt_id').filtered(
                lambda d: d.state not in ['invoiced', 'cancelled'] and d.invoice_option == 'billable'
            )
            order.qty_to_invoice_from_ddt = sum(ddt_to_invoice.mapped('ddt_lines.quantity'))

    # EXTRA FUNCTION

    def action_view_ddt(self):
        self.ensure_one()
        action = self.env.ref('l10n_it_ddt_extension_isa.action_l10n_it_ddt_extension_isa').read()[0]
        if self.ddt_count > 1:
            action['domain'] = [('id', 'in', self.ddt_ids.ids)]
        else:
            action['views'] = [(
                self.env.ref('l10n_it_ddt_extension_isa.l10n_it_ddt_extension_isa_view_form').id,
                'form'
            )]
            action['res_id'] = self.ddt_ids.id
        return action

    def prepare_ddt_values(self):
        """
        From picking create values for create ddt header.
        :return: dictionary of values
        """
        company = self.company_id.id or self.env.user.company_id.id
        # Get the default
        ddt_default = self.env['l10n_it.ddt'].default_get(['l10n_it_ddt_sequence', 'partner_type'])
        # prepare vals
        vals = {
            'date': fields.Date.today(),
            'partner_type': ddt_default['partner_type'],
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'incoterm_id': self.incoterm.id,
            'company_id': company,
            'goods_description_id': self.goods_description_id.id,
            'transportation_reason_id': self.transportation_reason_id.id,
            'transportation_method_id': self.transportation_method_id.id,
            'payment_term_id': self.payment_term_id.id,
            'l10n_it_ddt_sequence': ddt_default['l10n_it_ddt_sequence']
        }
        return vals
