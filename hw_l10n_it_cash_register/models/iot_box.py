# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class IotBox(models.Model):
    _inherit = 'iot.box'

    available_cash_register_ids = fields.One2many(
        string='Available cash register',
        comodel_name='base.cash.register',
        inverse_name='iot_box_id',
        help='List of all available cash register device',
        copy=False,
    )
