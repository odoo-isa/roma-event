# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountTax(models.Model):
    _inherit = "account.tax"

    account_tax_type = fields.Selection(
        selection_add=[
            ('cassa_previdenziale', 'Cassa Previdenziale'),
            ('withholding_tax', 'Withholding Tax')
        ]
    )

    withholding_payment_details = fields.Char(
        string='Withholding Payment Details',
        help='Code from 770S model',
    )

    cash_basis_transition_account_id = fields.Many2one(
        string="Transition account tax",
        help="Account used to transition the tax amount in exigibility on payment. It will contain the tax amount as "
             "long as the original invoice has not been reconciled; at reconciliation, this amount cancelled on this "
             "account and put on the regular tax account through a giro payment move."
    )
