# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    cig = fields.Char(
        string='CIG',
        size=15,
        copy=False,
        help="Indicates cig about partner"
    )

    cup = fields.Char(
        string='CUP',
        size=15,
        copy=False,
        help="Indicates cup about partner"
    )
