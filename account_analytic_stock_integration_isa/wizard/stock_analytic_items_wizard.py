# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


# Stock Analytic Item Wizard
# ---------------------------
class StockAnalyticItemsWizard(models.TransientModel):
    _name = 'stock.analytic.items.wizard'
    _description = 'Stock Analytic Items Wizard'

    # Prepare Account Analytic Line Based on Stock Move
    def prepare_analytic_line(self):
        today = fields.Datetime.now()
        year_start = today.replace(month=1, day=1, hour=0, minute=0, second=0).strftime(DATETIME_FORMAT)
        year_end = today.replace(month=12, day=31, hour=23, minute=59, second=59).strftime(DATETIME_FORMAT)
        stock_moves = self.env['stock.move'].search([('state', '=', 'done'),
                                                     ('location_id.analytic_account_id', '!=', False),
                                                     ('location_dest_id.analytic_account_id', '!=', False),
                                                     ('date', '>=', year_start),
                                                     ('date', '<=', year_end)])
        for each in stock_moves:
            if each.location_id.analytic_account_id:
                analytic_line = {
                    'name': each.name,
                    'product_id': each.product_id.id,
                    'product_uom_id': each.product_id.uom_id.id,
                    'account_id': each.location_id.analytic_account_id.id,
                    'amount': -1 * (each.product_id.standard_price * each.product_uom_qty),
                    'date': each.date,
                    'created_from_wizard': True
                }
                yield analytic_line
            if each.location_dest_id.analytic_account_id:
                analytic_line = {
                    'name': each.name,
                    'product_id': each.product_id.id,
                    'product_uom_id': each.product_id.uom_id.id,
                    'account_id': each.location_dest_id.analytic_account_id.id,
                    'amount': each.product_id.standard_price * each.product_uom_qty,
                    'date': each.date,
                    'created_from_wizard': True
                }
                yield analytic_line

    # Action Button to Create Account Analytic Line
    def action_build(self):
        analytic_items = self.env['account.analytic.line'].search([('created_from_wizard', '=', True)])
        if analytic_items:
            analytic_items.unlink()
        self.env['account.analytic.line'].create(list(self.prepare_analytic_line()))
