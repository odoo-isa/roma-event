# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    account_preferential_taxes_ids = fields.One2many(
        string='Preferential taxes',
        comodel_name='account.preferential.tax',
        inverse_name='res_partner_id',
        help="It indicates list of vat quotes about partner",
        copy=True,
        ondelete="cascade"
    )

    @api.constrains('account_preferential_taxes_ids')
    def _check_active_preferential_taxes(self):
        active_preferential_tax_ids = self.account_preferential_taxes_ids.filtered(
            lambda t: t.active_tax
        )
        if len(active_preferential_tax_ids) > 1:
            raise ValidationError(_("It's not possible to save because there are two or more active preferential taxes"))
