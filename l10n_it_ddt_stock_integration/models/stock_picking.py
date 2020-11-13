# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools import float_compare
from logging import getLogger

_logger = getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ddt_ids = fields.Many2many(
        string='Ddt',
        comodel_name='l10n_it.ddt',
        compute="_get_ddt",
        copy=False,
        store=True,
    )

    ddt_count = fields.Integer(
        string='# DdT',
        readonly=True,
        default=0,
        help="Number of DdT linked to picking.",
        copy=False,
        compute="_get_ddt",
        store=True
    )

    invoice_ids = fields.Many2many(
        string='Invoices',
        compute="_get_invoices",
        comodel_name='account.move'
    )

    invoice_count = fields.Integer(
        string='# of invoices',
        compute="_get_invoices"
    )

    can_create_ddt = fields.Boolean(
        string='Can Create DDT',
        compute="_get_can_create_ddt",
        store=True,
        help="Compute system field used for show or hide the create ddt button",
        copy=False,
        default=False
    )

    def _get_invoices(self):
        for picking in self:
            picking.invoice_ids = picking.mapped('move_lines.ddt_lines_ids.l10n_it_ddt_id.invoice_id')
            picking.invoice_count = len(picking.invoice_ids)

    @api.depends('move_lines.ddt_lines_ids')
    def _get_ddt(self):
        for picking in self:
            picking.ddt_ids = picking.mapped('move_lines.ddt_lines_ids.l10n_it_ddt_id.id')
            picking.ddt_count = len(picking.ddt_ids)

    @api.depends('partner_id', 'state', 'move_lines.ddt_lines_ids', 'picking_type_id', 'ddt_ids')
    def _get_can_create_ddt(self):
        """
        A picking, can create DdT if:
            - state is done
            - picking type is outgoing
            - partner is a customer or a supplier
            - state is done
            - there are move that not has linked DdT
        :return: bool
        """
        for picking in self:
            picking.can_create_ddt = False
            if picking.picking_type_id.code not in ('outgoing', 'internal'):
                continue
            if picking.state != 'done':
                continue
            if not picking.partner_id:
                continue
            if not picking.move_lines or all([len(move.ddt_lines_ids) > 0 for move in picking.move_lines]):
                continue
            to_invoice_qty = picking.move_lines._get_quantity_to_invoice()
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(to_invoice_qty, 0.0, precision_digits=precision) != 1:
                continue
            picking.can_create_ddt = True

    def prepare_ddt_values(self):
        """
        From picking create values for create ddt header.
        :return: dictionary of values
        """
        self.ensure_one()
        company = self.company_id.id or self.env.user.company_id.id
        type_of_operation = self.picking_type_id.code
        if type_of_operation == 'outgoing':
            partner_type = 'customer'
            payment_term_id = self.partner_id.property_payment_term_id.id
        elif type_of_operation == 'incoming':
            partner_type = 'supplier'
            payment_term_id = self.partner_id.property_supplier_payment_term_id.id
        elif type_of_operation == 'internal':
            partner_type = 'internal'
            payment_term_id = None
        else:
            raise ValidationError(_("Unable to create DdT for partner that aren't customer or supplier."))
        # prepare vals
        vals = {
            'partner_type': partner_type,
            'date': fields.Date.today(),
            'l10n_it_ddt_sequence': self.picking_type_id.l10n_it_ddt_sequence.id,
            'parcels': sum(self.mapped('parcels')),
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'incoterm_id': self.incoterm_id.id,
            'company_id': company,
            'goods_description_id': self.goods_description_id.id,
            'transportation_reason_id': self.transportation_reason_id.id,
            'transportation_method_id': self.transportation_method_id.id,
            'payment_term_id': payment_term_id,
            'location_id': self.location_id.id
        }
        return vals

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

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_move_line_form').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
