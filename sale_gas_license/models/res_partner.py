# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fgas_license = fields.Char(
        string='F-gas License',
        help='Indicates whether the partner has a license to sell fgas products ',
    )
