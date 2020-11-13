# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo.http import Controller, route, request
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)

class L10nItEdiControllerPreview(Controller):

    @route([
        '/l10n_it_edi/preview/<invoice_id>',
    ], type='http', auth='user', website=True)
    def pdf_preview(self, invoice_id, **data):
        acc_invoice_id = request.env['account.move'].browse(int(invoice_id))
        if acc_invoice_id.type in ('out_invoice', 'out_refund'):
            if not acc_invoice_id.l10n_it_einvoice_id:
                raise ValidationError(_('''Error. Is not possible to show the preview of the xml invoice because it is 
                not linked to this invoice. Please export the xml file and then click on Show Preview'''))
            attach_invoice_id = acc_invoice_id.l10n_it_einvoice_id
        else:
            invoice_attachment = request.env['ir.attachment'].search([
                ('res_model', 'like', 'account.move'),
                ('res_id', '=', acc_invoice_id.id),
                ('name', 'like', acc_invoice_id.l10n_it_einvoice_name)
            ], limit=1)
            attach_invoice_id = invoice_attachment[0] if invoice_attachment else None
        if not attach_invoice_id:
            raise ValidationError(_('No XML Invoice found.'))
        html = acc_invoice_id.get_fattura_elettronica_preview(attach_invoice_id)
        pdf = request.env['ir.actions.report']._run_wkhtmltopdf(
            [html])
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
