# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_incoterm(self):
        return self.env.user.company_id.incoterm_id

    goods_description_id = fields.Many2one(
        string='Description of Goods',
        comodel_name='l10n_it.goods_description',
        help='This field indicates the appearance of the goods',
        ondelete='restrict'
    )

    transportation_reason_id = fields.Many2one(
        string='Reason of Transportation',
        comodel_name='l10n_it.transportation_reason',
        ondelete='restrict',
        help='Reason for Transportation'
    )

    transportation_method_id = fields.Many2one(
        string='Method of Transportation',
        comodel_name='l10n_it.transportation_method',
        ondelete='restrict',
        help='Method of Transportation'
    )

    incoterm = fields.Many2one(
        string='Incoterm',
        help='International Commercial Terms are a series of predefined '
             'commercial terms used in international transactions.',
        comodel_name='account.incoterms',
        ondelete='restrict',
        default=_default_incoterm,
    )

    @api.onchange('partner_id')
    def delivery_options_onchange(self):
        self.goods_description_id = self.partner_id.goods_description_id
        self.transportation_reason_id = self.partner_id.transportation_reason_id
        self.transportation_method_id = self.partner_id.transportation_method_id
