# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    payment_type_id = fields.Many2one(
        string='Payment Type',
        comodel_name='payment.type',
        ondelete='set null',
        help="Indicates payment's type that will be used",
        copy=False
    )

    def _get_custom_data(self):
        self.ensure_one()
        res = super(AccountPaymentTermLine, self)._get_custom_data()
        res.update({'payment_type_id': self.payment_type_id.id})
        return res
