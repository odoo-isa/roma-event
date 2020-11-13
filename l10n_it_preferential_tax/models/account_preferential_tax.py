# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from logging import getLogger

_logger = getLogger(__name__)


class AccountPreferentialTax(models.Model):
    _name = "account.preferential.tax"
    _description = "Preferential tax"

    preferential_tax_id = fields.Many2one(
        string='Preferential tax',
        comodel_name='account.preferential.tax.type',
        help="The preferential tax that is applied for sale orders with destination at this delivery address.",
        copy=True
    )

    authorization_number = fields.Char(
        string='Authorization number',
        help="Authorization number",
        copy=True
    )

    released_date = fields.Date(
        string='Released',
        help="It indicates date validation from which odoo computes sale order line to compute",
        copy=True
    )

    expiration_date = fields.Date(
        string='Expiration',
        compute="_get_expiration_date",
        store=True,
        help="It indicates date validation until odoo computes sale order line to compute which",
        copy=True
    )

    self_declaration = fields.Binary(
        string='Self-declaration',
        help="Document to up and download about record vat quote",
        copy=False
    )

    file_name = fields.Char(
        string='File name',
        help="It's useful to document file to up and download",
        copy=False
    )

    active_tax = fields.Boolean(
        string='Active',
        help="We can decide if record will be compute for sale order line vat quote or not with this field",
        default=True,
        copy=False
    )

    res_partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        help="It is the inverse field to link vat quote to partner",
        copy=True
    )
    
    @api.depends('released_date')
    def _get_expiration_date(self):
        for record in self:
            if record.released_date:
                record.expiration_date = record.released_date + relativedelta(days=-1, years=1)

    def print_vat_quote(self):
        return self.env.ref('l10n_it_preferential_tax.vat_quote', raise_if_not_found=False).report_action(self)
