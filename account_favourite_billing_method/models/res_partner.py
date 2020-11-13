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

    favorite_billing_method = fields.Selection(
        string='Favorite billing method',
        required=True,
        default="all",
        selection=[('accompanying', 'Accompanying document'), ('deferred', 'Deferred Invoice'), ('all', 'All')],
        help="This field allows to choice a fixed method to create invoices for this specific partner",
        copy=True
    )

    deferred_billing_method = fields.Selection(
        string='Deferred billing method',
        default="standard",
        selection=[('standard', 'Standard'), ('ddt', 'One invoice for each DdT'),
                   ('delivery_adress', 'Group invoice by delivery adress')],
        help="This field, visible only if billing method is deferred, allows to choice if invoice must be grouped standard, or one for each DdT, or one for all DdT",
        copy=True
    )
