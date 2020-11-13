# -*- coding: utf-8 -*-
from odoo import api, fields, models


# Stock Location Model
# ----------------------
class StockLocation(models.Model):
    _inherit = 'stock.location'

    # Fields Declaration
    # -------------------
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')


# Account Analytic Line Model
# -----------------------------
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # Fields Declaration
    # -------------------
    created_from_wizard = fields.Boolean(string='Created From Stock Wizard')
