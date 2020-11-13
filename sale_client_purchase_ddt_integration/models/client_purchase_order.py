# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ClientPurchaseOrder(models.Model):
    _inherit = "client.purchase.order"

    ddt_ids = fields.Many2many(
        string='DDT',
        comodel_name='l10n_it.ddt',
        relation='ddt_id_client_purchase_order_id',
        column1='client_purchase_order_id',
        column2='ddt_id',
        help="It indicates list of ddt linked to client purhcase order",
        copy=True
    )
