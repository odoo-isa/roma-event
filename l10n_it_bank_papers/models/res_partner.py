# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    group_bank_papers_by_expiration = fields.Boolean(
        string='Group Bank Papers by Expiration',
        help="",
        copy=True
    )
