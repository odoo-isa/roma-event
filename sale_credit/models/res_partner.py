# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_credit_type = fields.Selection(
        string='Sale Credit Type',
        selection=[('unlimited', 'Unlimited'), ('value', 'Value')],
        default='value',
        help="Type of Credit, if unlimited, the customer is excluded of credit balace",
        track_visibility='onchange'
    )

    credit_limit = fields.Monetary(
        digits='Product Price',
        help="Credit limits of Partner",
        default=0.0,
        track_visibility='onchange'
    )

    remaing_credit = fields.Monetary(
        string='Remaing Credit',
        default=0.0,
        digits='Product Price',
        compute="_compute_sale_credit_type",
        readonly=True,
        help="It is calculated as Credit Value - (Accounting Balance + Ordered Value not Invoiced)"
    )

    def _compute_sale_credit_type(self):
        for partner in self:
            if partner.sale_credit_type == 'unlimited':
                partner.remaing_credit = 0.0
                return
            orders = self.env['sale.order'].search([('partner_id', '=', partner.id),('state', 'in', ['sale', 'done'])])
            total_amount_not_invoced = sum(orders.mapped('amount_not_invoiced'))
            # search all account_move_of_partner
            account_move_line = self.env['account.move.line'].search([
                ('account_id', '=', partner.property_account_receivable_id.id),
                ('partner_id', '=', partner.id)
            ])
            credit = sum(m.credit for m in account_move_line)
            debit = sum(m.debit for m in account_move_line)
            available_credit = partner.credit_limit - (debit - credit + total_amount_not_invoced)

            partner.remaing_credit = available_credit

