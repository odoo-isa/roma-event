# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools import float_is_zero
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class CreateDdtWizard(models.TransientModel):
    _name = 'create.ddt.from.sale.wizard'
    _description = 'Create Ddt'

    select_options = fields.Selection(
        string='Select Option',
        selection=[('create_ddt', 'Create new Ddt'), ('add_to_existing_ddt', 'Add to existing Ddt')]
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
        result = super(CreateDdtWizard, self).default_get(fields)
        order_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(order_id)
        result = self._default_get_data(sale_order, result)
        return result

    def _default_get_data(self, sale_id, result):
        if not sale_id:
            return result
        available_ddt = self.env['l10n_it.ddt'].search([
            ('partner_id', '=', sale_id.partner_id.id),
            ('state', '=', 'draft'),
            ('partner_shipping_id', '=', sale_id.partner_shipping_id.id),
            ('transportation_method_id', '=', sale_id.transportation_method_id.id),
            ('transportation_reason_id', '=',  sale_id.transportation_reason_id.id),
            ('goods_description_id', '=', sale_id.goods_description_id.id),
            ('incoterm_id', '=', sale_id.incoterm.id),
            ('payment_term_id', '=', sale_id.payment_term_id.id),
            ('partner_type', '=', 'customer')
        ])
        result['available_ddt'] = available_ddt.ids
        if available_ddt:
            result['select_options'] = 'add_to_existing_ddt'
        else:
            result['select_options'] = 'create_ddt'
        return result

    def create_ddt(self):
        """
        Method for show ddt. Can be called from sale_order or from picking.
        :return: ir.actions.act_window of created ddt
        """
        ddt_id = self._create_ddt()
        # Show the existing ddt or the new ddt
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference('l10n_it_ddt_extension_isa',
                                                      'l10n_it_ddt_extension_isa_view_form')
        form_id = form_res and form_res[1] or False
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'l10n_it.ddt',
            'res_id': ddt_id.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window'
        }

    def _create_ddt(self):
        """
        Method for create ddt.
        :return: ddt object
        """
        order_id = self.env.context.get('active_id')
        order = self.env['sale.order'].browse(order_id)
        ddt_id = None
        if self.select_options == 'add_to_existing_ddt':
            ddt_id = self.add_order_to_ddt(order)
        elif self.select_options == 'create_ddt':
            vals = order.prepare_ddt_values()
            # Create the Ddt header
            ddt_id = self.env['l10n_it.ddt'].create(vals)
            # Simulate the add_to_existing_ddt option for create line
            self.ddt_id = ddt_id.id
            self.add_order_to_ddt(order)
        return ddt_id

    def add_order_to_ddt(self, order):
        if not self.ddt_id:
            raise ValidationError(_("Unable to add picking to DdT. The destination DdT isn't specified"))
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        ddt_lines = []
        for line in order.order_line:
            quantity = line.get_quantity_available_for_ddt()
            if float_is_zero(quantity, precision_digits=precision):
                continue
            vals_line = line.prepare_ddt_values(quantity)
            ddt_lines.append((0, 0, vals_line))
        if not ddt_lines:
            raise ValidationError(_("There aren't order line to adding to DdT."))
        self.ddt_id.ddt_lines = ddt_lines
        return self.ddt_id
