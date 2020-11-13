# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class L10nItDdt(models.Model):

    _inherit = ["l10n_it.ddt"]

    carrier_id = fields.Many2one(
        string='Carrier',
        comodel_name='delivery.carrier',
        ondelete='restrict',
        states={
            'confirmed': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    def get_grouped_field_name(self) -> list:
        field_name = super(L10nItDdt, self).get_grouped_field_name()
        field_name.append('carrier_id')
        return field_name

    def get_grouped_field_value(self, journal_id=None) -> dict:
        field_value = super(L10nItDdt, self).get_grouped_field_value(journal_id)
        field_value['carrier_id'] = self.carrier_id.id
        return field_value
