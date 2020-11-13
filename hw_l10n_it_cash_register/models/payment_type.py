# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ClassName(models.Model):
    _inherit = 'payment.type'

    is_foregone_payment = fields.Boolean(
        string='IS foregone payment',
        help="Set this flag if this type of payment is a foregone payment",
        copy=False,
    )

    is_valid_retail_payment = fields.Boolean(
        string='Is a valid retail payment',
        help='''Check this flag if this payment type can be used in cash printer interface''',
        copy=True,
    )

    hydra_payment_code = fields.Integer(
        string='Payment code for Hydra cash register',
        default=0,
        help='''Hydra payment code as configured into the cash register parameters''',
        copy=False,
    )
