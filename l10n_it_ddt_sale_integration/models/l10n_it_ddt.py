# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class L10nItDdt(models.Model):
    _inherit = 'l10n_it.ddt'

    def unlink(self):
        """
        Recompute ddt field
        """
        orders = self.mapped('ddt_lines.sale_order_line_id.order_id')
        res = super(L10nItDdt, self).unlink()
        fields_list = [orders._fields[fname] for fname in ['ddt_ids', 'ddt_count','can_create_ddt']]
        for field in fields_list:
            self.env.add_to_compute(field, orders)
        return res

    def _add_extra_line(self, line_vals_list, move_id):
        installed_module = self.env['ir.module.module'].sudo().search([
            ('name', 'in', ['sale_raee']),
            ('state', '=', 'installed'),
        ])
        if installed_module:
            for line in self.ddt_lines:
                raee_line = self.add_raee_line(move_id,line)
                if not raee_line:
                    continue
                line_vals_list.append(raee_line)

        if not 'deduct_down_payments' in self.env.context and 'has_down_payment' in self.env.context:
            pass
        down_payment_line = self.mapped('ddt_lines.sale_order_line_id.order_id.order_line').filtered(lambda l: l.is_downpayment)
        if down_payment_line and self.env.context['deduct_down_payments']:
            deduct_total = down_payment_line.mapped('price_unit')[0]
            product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
            product_tmpl_id = self.env['product.product'].browse(int(product_id)).product_tmpl_id
            account_id = None
            if product_tmpl_id.property_account_income_id:
                account_id = product_tmpl_id.property_account_income_id.id
            elif product_tmpl_id.categ_id and product_tmpl_id.categ_id.property_account_income_id:
                account_id = product_tmpl_id.categ_id.property_account_income_id.id
            invoice_line = {
                'name': _('Down Payment'),
                'product_id': int(product_id),
                'quantity': -1,
                'price_unit': deduct_total,
                'move_id': move_id,
                'account_id': account_id,
                'tax_ids': [(6, 0, down_payment_line.tax_id.ids)]
            }

            line_vals_list.append(invoice_line)

    def add_raee_line(self,move_id, line):
        if not line.sale_order_line_id.link_with_raee:
            return False
        move_obj = self.env['account.move'].browse(move_id)
        link_raee = line.sale_order_line_id.link_with_raee
        if not link_raee.qty_delivered:
            return
        result = link_raee.qty_delivered - link_raee.qty_invoiced
        if result == 0:
            return
        if move_obj.type == 'out_invoice':
            account_id = link_raee.product_id.property_account_income_id or link_raee.product_id.categ_id.property_account_income_categ_id
            if not account_id:
                account_id = self.env['account.move.line'].with_context(default_type=self._context['type']).default_get(['account_id'])
                account_id = self.env['account.account'].browse(account_id.get('account_id', False))
                if not account_id:
                    raise UserError(
                        _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                        (link_raee.product_id.name, link_raee.product_id.id, link_raee.product_id.categ_id.name))

        elif move_obj.type == 'out_refund':
            account_id = link_raee.product_id.property_account_expense_id or link_raee.product_id.categ_id.property_account_expense_categ_id
            if not account_id:
                account_id = self.env['account.move.line'].with_context(default_type=self._context['type']).default_get(['account_id'])
                account_id = self.env['account.account'].browse(account_id.get('account_id', False))
                if not account_id:
                    raise UserError(
                        _('Please define expense account for this product: "%s" (id:%d) - or for its category: "%s".') %
                        (link_raee.product_id.name, link_raee.product_id.id, link_raee.product_id.categ_id.name))

        return {
            'name': link_raee.name,
            'product_id': link_raee.product_id.id,
            'quantity': result,
            'price_unit': link_raee.price_unit,
            'move_id': move_id,
            'account_id': account_id.id,
            'tax_ids': [(6, 0, link_raee.tax_id.ids)]
        }
