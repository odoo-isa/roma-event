# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from logging import getLogger

_logger = getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    related_document_line_ids = fields.One2many(
        string='Related Documents',
        required=False,
        readonly=False,
        comodel_name='l10n_it_edi.related_document',
        inverse_name='move_line_id',
        help="Represent related document associated to the move",
        copy=False,
    )

    @api.constrains('tax_ids')
    def _check_vat_tax_italy(self):
        for invoice_line in self:
            if len(invoice_line.tax_ids.filtered(lambda t: t.account_tax_type == 'vat_tax')) > 1:
                raise UserError(_("You must select one and only one tax by line."))
