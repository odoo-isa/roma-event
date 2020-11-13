# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class DdtAdvancePaymentInvoice(models.TransientModel):
    _inherit = 'ddt.advance.payment.invoice.wizard'

    @api.model
    def _default_has_down_payment(self):
        if self._context.get('active_model') == 'l10n_it.ddt' and self._context.get('active_ids', False):
            ddt_id = self.env['l10n_it.ddt'].browse(self._context.get('active_ids'))
            return ddt_id.mapped('ddt_lines.sale_order_line_id.order_id.order_line').\
                filtered(lambda l: l.is_downpayment)
        return False

    deduct_down_payments = fields.Boolean(
        string='Deduct down payments',
        default=True
    )

    has_down_payments = fields.Boolean(
        string='Has down payments',
        default=_default_has_down_payment,
        readonly=True
    )

    message = fields.Html(
        string='Message',
        required=False,
        readonly=True,
        help='This field is used to show which tuple of order and DDT have a down payment associated, usefull to decide '
             'if deduct it or not.',
        copy=False,
        compute='compute_message'
    )

    def create_invoices(self):
        return super(DdtAdvancePaymentInvoice, self.with_context(deduct_down_payments=self.deduct_down_payments,
                                                                    has_down_payment=self.has_down_payments)).create_invoices()

    @api.model
    @api.depends('has_down_payments')
    def compute_message(self):
        for record in self:
            record.message = ''
            if record.has_down_payments:
                order_ids = record._get_order_info()
                template_view = self.env.ref('l10n_it_ddt_sale_integration.down_payment_template', None)
                html = _("Error during result view.")
                if template_view:
                    html = template_view.render(values={
                        'order_ids': order_ids,
                    })
                record.message = html

    def _get_order_info(self):
        res = []
        if self._context.get('active_model') == 'l10n_it.ddt' and self._context.get('active_id', False):
            ddt_ids = self.env['l10n_it.ddt'].browse(self._context.get('active_ids'))
            for ddt_id in ddt_ids:
                order_line = ddt_id.mapped('ddt_lines.sale_order_line_id.order_id.order_line'). \
                    filtered(lambda l: l.is_downpayment)
                for line in order_line:
                    dict_line = {
                        'partner': ddt_id.partner_id.name if ddt_id.partner_id else line.order_id.partner_id.name,
                        'order_number': line.order_id.name,
                        'ddt_number': ddt_id.name,
                        'amount': line.price_unit
                    }
                    res.append(dict_line)
        return res
