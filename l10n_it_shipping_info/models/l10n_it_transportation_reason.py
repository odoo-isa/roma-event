# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class L10nItTransportationReason(models.Model):
    _name = 'l10n_it.transportation_reason'
    _description = 'Transportation Reason'

    name = fields.Char(
        string='Reason for Transportation',
        required=True,
    )

    note = fields.Text(
        string='Note',
    )
