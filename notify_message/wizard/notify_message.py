# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class NotifyMessage(models.TransientModel):
    _name = 'notify.message.wizard'
    _description = "Notify Message"

    text = fields.Html(
        string='Text Message',
        readonly=True
    )

    def close(self):
        return {
            'type': 'ir.actions.act_window_close'
        }

