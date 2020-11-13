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

    bank_reconciliation_threshold = fields.Float(
        string='Bank reconciliation threshold',
        related='company_id.bank_reconciliation_threshold',
        readonly=False,
        digits='Product Price',
        help='''Will be raise a warning message if will be exceed this value during payment matching. This check will be
        performed only if there is deficit between credit and debit and if the writeoff account has been specified.''',
    )
