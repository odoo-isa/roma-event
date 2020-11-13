# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class PaymentType(models.Model):
    _inherit = 'payment.type'

    l10n_it_edi_payment_method = fields.Selection(
        string='Electronic Invoice Payment Method',
        required=False,
        readonly=False,
        default=False,
        selection=[
            ('MP01', 'Contanti'),
            ('MP02', 'Assegno'),
            ('MP03', 'Assegno Circolare'),
            ('MP04', 'Contanti presso Tesoreria'),
            ('MP05', 'Bonifico'),
            ('MP06', 'Vaglia cambiario'),
            ('MP07', 'Bollettino bancario'),
            ('MP08', 'Carta di Pagamento'),
            ('MP09', 'RID'),
            ('MP10', 'RID Utenze'),
            ('MP11', 'RID veloce'),
            ('MP12', 'RIBA'),
            ('MP13', 'MAV'),
            ('MP14', 'Quietanza erario'),
            ('MP15', 'Giroconto su conti di contabilità speciale'),
            ('MP16', 'Domiciliazione bancaria'),
            ('MP17', 'Domiciliazione postale'),
            ('MP18', 'Bollettino di c/c postale'),
            ('MP19', 'SEPA Direct Debit'),
            ('MP20', 'SEPA Direct Debit CORE'),
            ('MP21', 'SEPA Direct Debit B2B'),
            ('MP22', 'Trattenuta su somme già riscosse'),
            ('MP23', 'PagoPA')

        ],
        copy=True,
    )
