# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api


class AccountDueDateWizard(models.TransientModel):
    _name = 'account.due.date.wizard'
    _description = 'Account Due Date Wizard'

    due_date = fields.Date(
        string='Due Date',
        help='Due Date of move line',
    )

    payment_type_id = fields.Many2one(
        string='Payment Type',
        help="Payment Type of move line",
        comodel_name='payment.type',
    )

    amount = fields.Float(
        string='Amount',
        help="Amount of move line"
    )
