# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields
from logging import getLogger

_logger = getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    create_and_send_einvoices_in_separate_steps = fields.Boolean(
        string='Creation and Sending of Electronic Invoices in separate steps',
        help="If set, allows to edit basic behavior of invoice validation: only the invoice is valid."
             "Then user can use the Generate Electronic Invoice button to generate the electronic invoice.",
        copy=False
    )

    fatturapa_art73 = fields.Boolean(
        string='Art73',
        help="indicates whether the document has been issued in accordance "
             "with the terms and conditions established by ministerial "
             "decree in accordance with Article 73 of Presidential Decree"
             ""
             "633/72 (this allows the company to issue the same"
             " year more documents with the same number)",
        copy=False,
    )

    fatturapa_sequence = fields.Many2one(
        string='Fattura PA sequence',
        readonly=False,
        copy=False,
        comodel_name='ir.sequence',
        help='This field is a link to the sequence used to set progressive number on invoice xml when file is '
             'generated',
        default=lambda self: self.env.ref('l10n_it_edi_extension_isa.fatturapa_seq', raise_if_not_found=False)
    )

    l10n_it_edi_preview_style = fields.Selection(
        string='Preview Format Style',
        selection=[
            ('fatturaordinaria_v1.2.1.xsl', 'FatturaOrdinaria v1.2.1'),
            ('FoglioStileAssoSoftware_v1.1.xsl', 'AssoSoftware v1.1')
        ],
        default='fatturaordinaria_v1.2.1.xsl',
        help='',
        copy=False,
    )
