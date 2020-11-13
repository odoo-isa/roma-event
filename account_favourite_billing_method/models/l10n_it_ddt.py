# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class L10nItDdt(models.Model):
    _inherit = 'l10n_it.ddt'

    def get_grouped_field_name(self) -> list:
        field_name = super(L10nItDdt, self).get_grouped_field_name()
        if self.partner_id.deferred_billing_method == 'delivery_adress':
            field_name.append('partner_shipping_id')
        if self.partner_id.deferred_billing_method == 'ddt':
            field_name.append('id')
        return field_name

    def get_grouped_field_value(self, journal_id=None) -> dict:
        field_value = super(L10nItDdt, self).get_grouped_field_value(journal_id=journal_id)
        if self.partner_id.deferred_billing_method == 'delivery_adress':
            field_value['partner_shipping_id'] = self.partner_shipping_id.id
        if self.partner_id.deferred_billing_method == 'ddt':
            field_value['id'] = self.id
        return field_value
