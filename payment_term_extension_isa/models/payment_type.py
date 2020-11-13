# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class PaymentType(models.Model):
    _name = 'payment.type'
    _description = "Payment Type"

    name = fields.Char(
        string='Name',
        required=True,
        help="Indicates name of payment's type"
    )

    code = fields.Char(
        string='Code',
        required=True,
        help="Indicates code of payment's type"
    )

