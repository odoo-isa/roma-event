# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools import float_is_zero
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class CreateDdTFromStockWizard(models.TransientModel):
    _name = 'create.ddt.from.stock.wizard'
    _description = 'Create Ddt from stock'

    select_options = fields.Selection(
        string='Select Option',
        selection=[('create_ddt', 'Create Ddt'), ('add_to_existing_ddt', 'Add Pickings to Ddt')]
    )

    available_ddt = fields.Many2many(
        string='Available DdT',
        help="System Field's for calculate available ddt.",
        readonly=True,
        comodel_name='l10n_it.ddt',
    )

    ddt_id = fields.Many2one(
        string='Ddt',
        comodel_name='l10n_it.ddt',
    )

    @api.model
    def default_get(self, fields):
        """
        This method is used for initialize data wizard to create ddt.
        Suggest to create new ddt if there aren't ddt with congruent data.
        Suggest to adding to existing ddt if there are one or more ddt with congruency.
        :param fields:
        :return: dictionary of default.
        """
        result = super(CreateDdTFromStockWizard, self).default_get(fields)
        picking = self.env.context.get('active_ids')
        picking = self.env['stock.picking'].browse(picking)
        if picking.state != 'done':
            return result
        picking = picking.move_lines.filtered(lambda l: not l.ddt_lines_ids).mapped('picking_id')
        if not picking:
            return result
        picking.ensure_one()
        result = self._default_get_data(picking, result)
        return result

    def _default_get_data(self, picking, result):
        # Check if picking is customer or supplier
        type_of_operation = picking.picking_type_id.code
        if type_of_operation == 'outgoing':
            partner_type = 'customer'
            payment_term_id = picking.partner_id.property_payment_term_id.id
        elif type_of_operation == 'incoming':
            partner_type = 'supplier'
            payment_term_id = picking.partner_id.property_supplier_payment_term_id.id
        elif type_of_operation == 'internal':
            partner_type = 'internal'
            payment_term_id = None
        else:
            return result
        available_ddt = self._get_available_ddt(picking, payment_term_id, partner_type)
        if available_ddt:
            result['available_ddt'] = available_ddt.ids
            result['select_options'] = 'add_to_existing_ddt'
        else:
            result['select_options'] = 'create_ddt'
        return result

    def _get_available_ddt(self, picking, payment_term_id, partner_type):
        partner_id = picking.partner_id.parent_id if picking.partner_id.parent_id else picking.partner_id
        available_ddt = self.env['l10n_it.ddt'].search([
            ('partner_id', '=', partner_id.id),
            ('state', '=', 'draft'),
            ('partner_shipping_id', '=', picking.partner_id.id),
            ('transportation_method_id', '=', picking.transportation_method_id.id),
            ('transportation_reason_id', '=', picking.transportation_reason_id.id),
            ('goods_description_id', '=', picking.goods_description_id.id),
            ('payment_term_id', '=', payment_term_id),
            ('location_id', '=', picking.location_id.id),
            ('partner_type', '=', partner_type)
        ])
        return available_ddt

    def create_ddt(self):
        """
        Method for show ddt. Can be called from sale_order or from picking.
        :return: ir.actions.act_window of created ddt
        """
        self.ensure_one()
        ddt = self._create_ddt()
        # Show the existing ddt or the new ddt
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference('l10n_it_ddt_extension_isa',
                                                      'l10n_it_ddt_extension_isa_view_form')
        form_id = form_res and form_res[1] or False
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_it.ddt',
            'res_id': ddt.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window'
        }

    def _create_ddt(self):
        """
        Method for create ddt.
        :return: ddt object
        """
        # Ddt can be created from sale.order or stock.picking
        picking_ids = self.env.context.get('active_ids')
        picking_obj = self.env['stock.picking'].browse(picking_ids)
        picking_obj.ensure_one()
        ddt_id = None
        if self.select_options == 'create_ddt':
            vals = picking_obj.prepare_ddt_values()
            # Create the Ddt header
            ddt_id = self.env['l10n_it.ddt'].create(vals)
            # Simulate the add_to_existing_ddt option for create line
            self.ddt_id = ddt_id.id
            self.add_picking_to_ddt(picking_obj)
        elif self.select_options == 'add_to_existing_ddt':
            ddt_id = self.add_picking_to_ddt(picking_obj)
        return ddt_id

    def add_picking_to_ddt(self, picking_obj):
        if not self.ddt_id:
            raise ValidationError(_("Unable to add picking to DdT. The destination DdT isn't specified"))
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        ddt_lines = []
        for move in picking_obj.move_lines:
            quantity = move._get_quantity_to_invoice()
            if float_is_zero(quantity, precision_digits=precision):
                continue
            type_of_operation = picking_obj.picking_type_id.code
            partner_type = None
            if type_of_operation == 'outgoing':
                partner_type = 'customer'
            elif type_of_operation == 'incoming':
                partner_type = 'supplier'
            vals_line = move.prepare_ddt_values(quantity, partner_type)
            ddt_lines.append((0, 0, vals_line))
        if not ddt_lines:
            raise ValidationError(_("There aren't move line to adding to DdT."))
        self.ddt_id.ddt_lines = ddt_lines
        return self.ddt_id
