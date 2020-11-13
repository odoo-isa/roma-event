# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields
from logging import getLogger

_logger = getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

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

    def address_get(self, adr_pref=None):
        res = super(ResPartner, self).address_get(adr_pref=adr_pref)
        set_partner_shipping = self._context.get('set_partner_shipping', None)
        partner_shipping_id = self._context.get('partner_shipping_id', None)
        if set_partner_shipping and partner_shipping_id:
            res['delivery'] = partner_shipping_id.id
        return res
