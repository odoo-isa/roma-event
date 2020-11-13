# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    withholding_payment_term = fields.Many2one(
        string='Withholding payment term',
        comodel_name='account.payment.term',
        help='''This value will be set in the withholding move that will be created when tax exigibility will be 
        triggered''',
        copy=False,
        ondelte='restrict'
    )

    withholding_journal_id = fields.Many2one(
        string='Withholding Journal',
        comodel_name='account.journal',
        ondelete='restrict',
        help='''This value will be set in the withholding move that will be created when tax exigibility will be 
        triggered''',
        copy=False,
    )
