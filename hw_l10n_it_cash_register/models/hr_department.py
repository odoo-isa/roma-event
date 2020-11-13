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
    _inherit = 'hr.department'

    iot_box_id = fields.Many2one(
        string='IOT Box',
        comodel_name='iot.box',
        ondelete='set null',
        help='Set which IOT BOX is assigned',
        copy=False,
    )
