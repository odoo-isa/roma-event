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
    _inherit = 'account.move'

    invoice_mode = fields.Selection(selection_add=[('deferred', 'Deferred Invoice')])

    ddt_ids = fields.One2many(
        string='Linked DDT',
        comodel_name='l10n_it.ddt',
        inverse_name='invoice_id'
    )

    def unlink(self):
        self.mapped('ddt_ids').write({'state': 'confirmed'})
        res = super(AccountMove, self).unlink()
        return res

    def _compute_delivery_expense(self, precision):
        pass
