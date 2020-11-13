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

    ddt_id = fields.Many2one(
        string='DdT',
        readonly=False,
        comodel_name='l10n_it.ddt',
    )

    ddt_line_id = fields.Many2one(
        string='DdT Line',
        comodel_name='l10n_it.ddt.line',
        ondelete="restrict",
        help="Reference to DdT line",
        copy=False,
    )