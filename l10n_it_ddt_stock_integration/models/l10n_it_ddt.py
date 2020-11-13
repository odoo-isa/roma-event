# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class L10NItDdT(models.Model):
    _inherit = 'l10n_it.ddt'

    ddt_lines_return = fields.Many2many(
        string='Returned Ddt Line',
        readonly=True,
        help=False,
        comodel_name='stock.move',
        compute='_get_lines_return'
    )

    picking_returned_count = fields.Integer(
        string='Picking Returned Count',
        compute='_compute_picking_returned_ids'
    )

    location_id = fields.Many2one(
        string='Location',
        help=False,
        comodel_name='stock.location',
        ondelete='restrict',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    def unlink(self):
        """
        Recompute ddt field
        """
        pickings = self.mapped('ddt_lines.stock_move_id.picking_id')
        res = super(L10NItDdT, self).unlink()
        fields_list = [pickings._fields[fname] for fname in ['ddt_ids', 'ddt_count', 'can_create_ddt']]
        for field in fields_list:
            self.env.add_to_compute(field, pickings)
        return res

    def _get_lines_return(self):
        for record in self:
            record.ddt_lines_return = False
            returned_move = self.env['stock.move'].search([
                ('origin_returned_move_id', 'in', self.mapped('ddt_lines.stock_move_id').ids)
            ])
            if returned_move:
                record.ddt_lines_return = returned_move

    def _compute_picking_returned_ids(self):
        for ddt in self:
            picking_returned = ddt.ddt_lines_return.mapped('picking_id')
            ddt.picking_count = len(picking_returned)

    def get_grouped_field_name(self) -> list:
        field_name = super(L10NItDdT, self).get_grouped_field_name()
        field_name.append('location_id')
        return field_name

    def get_grouped_field_value(self, journal_id=None) -> dict:
        field_value = super(L10NItDdT, self).get_grouped_field_value(journal_id)
        field_value['location_id'] = self.location_id.id
        return field_value


