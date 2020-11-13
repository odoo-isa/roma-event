# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import re
from odoo import models, fields, api
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    receipt_number = fields.Integer(
        string='Receipt number',
        readonly=True,
        index=True,
        help="The number of the receipt from the cash register",
        copy=False,
    )

    def print_bill(self):
        self.ensure_one()
        # The order have to be in sale state
        if self.state != 'sale':
            raise UserError(_("In order to print bill the order must be confirmed."))
        # The order shouldn't have already a linked receipt
        if self.receipt_number:
            raise UserError(_("A receipt is already present. Number receipt %d") % self.receipt_number)
        return {
            "type": "ir.actions.client",
            "tag": "micrelec_hydra_bill",
            "name": "Print Bill",
            "params": {
                'sale_order': self.id,
                'precision': self.env['decimal.precision'].precision_get('Product Price')
            },
            "target": "new"
        }

    def get_sale_order_cash_ticket(self):
        """
        Print sale order in cash bill layout.
        :return: string html
        """
        # Retrieve all payment type valid for retail
        payment_type = self.env['payment.type'].search([('is_valid_retail_payment', '=', True)])
        html = self.env['ir.ui.view'].render_template(
            "hw_l10n_it_cash_register.sale_order_cash_ticket",
            values={
                'company': self.env.user.company_id,
                'sale_order': self,
                'currency': self.env.user.currency_id,
                'payments': payment_type,
            }
        )
        return html

    def get_print_bill_commands(self, payment_info):
        self.ensure_one()
        commands = []
        precision = self.env['decimal.precision'].precision_get('Product Price')
        for line in self.order_line:
            # Search for the department, retrieve the tax type.
            vat = line.tax_id.filtered(lambda t: t.account_tax_type == 'vat_tax')
            if len(vat) != 1:
                raise UserError(_("Must be present only one VAT"))
            if not vat.cash_department:
                raise UserError(_("Must be set the department for vat %s") % vat.name)
            # Compute price unit VAT included
            price_unit = line.price_unit * (1 - (line.discount / 100.0))  # Compute amount with discount
            price_vat = line.tax_id.compute_all(price_unit=price_unit, quantity=1)
            total_included = float_round(price_vat['total_included'], precision_digits=precision)
            total_included = round(total_included, precision)
            command = f"3/S/{line.product_id.name[:30]}//{line.product_uom_qty}/{total_included}/{vat.cash_department}/////"
            commands.append(command)
        commands.append('U/')  # Command for calculate subtotal
        # Retrieve payment info
        for payment in payment_info:
            match = re.match(r'payment\[\'(.*)\']', payment['name'])
            if not match:
                continue
            payment_code = int(match.group(1))
            payment_value = float(payment['value'].replace(',', '.'))
            command = f"5/{payment_code}/{payment_value}//////"
            commands.append(command)
        commands.append('0/')  # Read daily total
        commands.append('i/')  # Read fiscal data
        commands.append('=/')  # Cutter
        return commands
