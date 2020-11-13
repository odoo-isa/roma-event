# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields
from logging import getLogger

_logger = getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    create_and_send_einvoices_in_separate_steps = fields.Boolean(
        string='Creation and Sending of Electronic Invoices in separate steps',
        related='company_id.create_and_send_einvoices_in_separate_steps',
        readonly=False
    )

    fatturapa_art73 = fields.Boolean(
        string="Art73",
        related='company_id.fatturapa_art73',
        readonly=False
    )

    fatturapa_sequence = fields.Many2one(
        string='Fattura PA sequence',
        readonly=False,
        related='company_id.fatturapa_sequence'
    )

    l10n_it_edi_preview_style = fields.Selection(
        string='Preview Format Style',
        help='',
        copy=False,
        readonly=False,
        related='company_id.l10n_it_edi_preview_style'
    )
