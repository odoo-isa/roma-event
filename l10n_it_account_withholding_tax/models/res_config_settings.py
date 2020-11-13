# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    withholding_payment_term = fields.Many2one(
        string='Withholding payment term',
        related='company_id.withholding_payment_term',
        readonly=False
    )

    withholding_journal_id = fields.Many2one(
        string='Withholding Journal',
        related='company_id.withholding_journal_id',
        readonly=False
    )
