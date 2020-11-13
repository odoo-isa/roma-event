# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class L10nItTransportationMethod(models.Model):
    _name = 'l10n_it.transportation_method'
    _description = 'Transportation Method'

    name = fields.Char(
        string='Transportation Method',
        required=True,
    )

    note = fields.Text(
        string='Note',
    )
