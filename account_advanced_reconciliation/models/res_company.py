# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields
from logging import getLogger

_logger = getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    bank_reconciliation_threshold = fields.Float(
        string='Bank reconciliation threshold',
        digits='Product Price',
        help='''Will be raise a warning message if will be exceed this value during payment matching. This check will be
        performed only if there is deficit between credit and debit and if the writeoff account has been specified.''',
    )
