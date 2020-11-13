# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields
from logging import getLogger

_logger = getLogger(__name__)


class L10nItGoodsDescription(models.Model):
    _name = 'l10n_it.goods_description'
    _description = 'Description'

    name = fields.Char(
        string='Description of Goods',
        required=True,
    )

    note = fields.Text(
        string='Note',
    )
