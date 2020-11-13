# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    default = fields.Boolean(
        string='Default',
        help='',
    )
