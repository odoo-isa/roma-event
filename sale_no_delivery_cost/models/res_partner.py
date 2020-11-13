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

    not_delivery_outgoing = fields.Boolean(
        string='Not delivery outgoing',
        help="It set invisible button to add delivery in sale order",
        copy=True
    )
