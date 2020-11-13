# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tests.common import Form


class ImportInvoiceImportWizard(models.TransientModel):
    _name = 'account.invoice.import.wizard'
    _description = 'Import Your Vendor Bills from Files.'

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Files'
    )

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        domain=[('type', '=', 'purchase')],
        required=True,
        help="Journal where to generate the bills"
    )

    def _create_invoice_from_file(self, attachment):
        self = self.with_context(default_journal_id= self.journal_id.id)
        invoice_form = Form(self.env['account.move'], view='account.view_move_form')
        invoice = invoice_form.save()
        attachment.write({'res_model': 'account.move', 'res_id': invoice.id})
        invoice.message_post(attachment_ids=[attachment.id])
        return invoice

    def create_invoices(self):
        ''' Create the invoices from files.
         :return: A action redirecting to account.invoice tree/form view.
        '''
        if not self.attachment_ids:
            return
        attachent_found = self.env['account.move'].search([('l10n_it_einvoice_name', 'in', self.mapped('attachment_ids.display_name')),
                                            ('journal_id', '=', self.journal_id.id)])
        if attachent_found:
            raise ValidationError(_('Error! Is not possibile to import multiple time the same invoice. '
                                    'Invalid xml uploaded: %s' % (', '.join(attachent_found.mapped('l10n_it_einvoice_name')))))
        return self.env['account.journal'].with_context(default_type='in_invoice').create_invoice_from_attachment(self.attachment_ids.ids)