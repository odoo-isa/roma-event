# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    ddt_in = fields.Char(
        string='''Supplier's Ddt''',
        help='''Supplier's Ddt''',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        copy=False,
    )
