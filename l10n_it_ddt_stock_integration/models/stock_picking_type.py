# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    l10n_it_ddt_sequence = fields.Many2one(
        string='DDT Sequence',
        comodel_name='ir.sequence',
        default=lambda self: self.env.ref('l10n_it_ddt_extension_isa.seq_ddt', raise_if_not_found=False),
    )
