# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_mode = fields.Selection(selection_add=[('accompanying', "Accompanying Invoice")])

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
