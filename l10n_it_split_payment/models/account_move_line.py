# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_split_line = fields.Boolean(
        string='Is Split Line',
        help='Technical field used to identify the split payment line.',
        copy=False,
    )
