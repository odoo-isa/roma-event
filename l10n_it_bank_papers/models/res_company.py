# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    sia_code = fields.Char(
        string='SIA Code',
        help='''It identifies the exchanges that devices want to exchange, informative with their treasury banks
                in compliance with the CBI service rules. It consists of a letter and 4 numbers''',
        copy=True
    )
