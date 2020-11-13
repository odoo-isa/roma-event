# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains('invoice_mode')
    def check_invoice_validity(self):
        if self.type in ['out_invoice', 'in_invoice'] and self.partner_id.favorite_billing_method not in ['all', self.invoice_mode]:
            raise ValidationError(_("Error invoice creating. Partner favorite billing method doesn't allow to create invoice"))
