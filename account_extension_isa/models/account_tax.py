# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    account_tax_type = fields.Selection(
        string='Account tax type',
        selection=[
            ('vat_tax', 'VAT Tax'),
            ('other_tax', 'Other Tax')
        ],
        default="vat_tax",
        help="What kind of tax this record rapresent",
        copy=True
    )
