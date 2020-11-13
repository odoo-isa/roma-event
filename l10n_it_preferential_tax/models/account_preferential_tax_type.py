# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountPreferentialTaxType(models.Model):
    _name = "account.preferential.tax.type"
    _description = "Preferential tax type"

    name = fields.Char(
        string='Name',
        required=True,
        help="Name of preferential tax type",
        copy=True
    )

    tax_id = fields.Many2one(
        string='Tax',
        comodel_name='account.tax',
        required=True,
        help="Tax",
        copy=True
    )

    invoice_description = fields.Char(
        string='Invoice description',
        help="Description of invoice",
        copy=True
    )
