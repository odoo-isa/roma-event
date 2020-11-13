# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class SelectPaymentTypeWizard(models.TransientModel):
    _name = 'select.payment.type.wizard'
    _description = 'Select Payment Type'

    payment_type_id = fields.Many2one(
        string='Choose Payment Type',
        required=True,
        readonly=False,
        comodel_name='payment.type',
        help="It allows to choose payment type to filter the search of results",
        copy=True
    )

    def search_account_move_line(self):
        """
        filter account move line because of payment type
        :return: a form view to show account move line
        """
        for record in self:
            move_line = record.env['account.move.line'].get_account_move_line_for_riba(record.payment_type_id)
            list_view = self.env.ref('account.view_move_line_tree')
            return {
                'name': _('Slip'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move.line',
                'views': [[list_view.id, 'list'], [False, 'form']],
                'domain': [('id', 'in', move_line.ids),('parent_state', 'not in', ['draft','cancel'])],
                'target': 'current'
            }
