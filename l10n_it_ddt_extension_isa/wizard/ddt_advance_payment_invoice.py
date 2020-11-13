# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class DdtAdvancePaymentInvoice(models.TransientModel):
    _name = 'ddt.advance.payment.invoice.wizard'
    _description = 'Ddt Advance Payment Invoice'

    invoice_date = fields.Date(
        string='Invoice Date',
        required=True,
        default=fields.Date.today(),
        help='Invoice Registration Date',
    )

    journal_id = fields.Many2one(
        string='Journal',
        required=True,
        help=False,
        comodel_name='account.journal',
        ondelete='restrict',
        domain=[('type', '=', 'sale')],
    )

    def create_invoices(self):
        ddt_ids = self.env.context.get('active_ids')
        list_ddt_obj = self.env['l10n_it.ddt'].browse(ddt_ids)
        list_ddt_obj = list_ddt_obj.filtered(lambda d: d.invoice_option == 'billable')
        if not list_ddt_obj:
            raise ValidationError("There aren't DDT to be invoiced")
        # Checking if a 'Dictionary' is empty
        ddt_to_not_invoice = list_ddt_obj.invoice_preliminary_check(self.invoice_date)
        if bool(ddt_to_not_invoice):
            res_id = self.env['notify.message.wizard'].create({
                'text': self._compose_error_message(ddt_to_not_invoice)
            })
            return {
                "type": "ir.actions.act_window",
                "res_model": "notify.message.wizard",
                "views": [[False, "form"]],
                "res_id": res_id.id,
                "target": "new",
            }
        invoices = list_ddt_obj.action_invoice_create(self.invoice_date, journal_id=self.journal_id)
        invoices_obj = self.env['account.move'].browse(invoices)
        if self._context.get('open_invoices', False):
            return list_ddt_obj.action_view_invoice(invoices_obj)
        return {'type': 'ir.actions.act_window_close'}

    def _compose_error_message(self, dict):
        error_message = self.env['ir.ui.view'].render_template(
            "l10n_it_ddt_extension_isa.ddt_invoice_errors",
            values={
                'errors': dict
            },
        )
        return error_message
