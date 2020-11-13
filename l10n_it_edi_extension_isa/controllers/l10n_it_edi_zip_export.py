# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
try:
    import json
except ImportError:
    import simplejson as json

from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import UserError
import zipfile
import base64
import io


class ExportFatturePAZipFIle(http.Controller):

    def _generate_zipped_file(self, invoices):
        """ Function to generate a zip file containing all e-invoices xml
        :param invoices: Invoices's RecordSet
        :return: binary data, using for create a download file
        """
        in_memory_zip = io.BytesIO()
        zf = zipfile.ZipFile(in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
        for invoice in invoices:
            # Invoice's Supplier or Credit Note
            if invoice.type == 'in_invoice' or invoice.type == 'in_refund':
                invoice_attachment = invoice.env['ir.attachment'].search([
                    ('res_model', 'like', 'account.move'),
                    ('res_id', '=', invoice.id),
                    ('name', 'like', invoice.l10n_it_einvoice_name)
                ], limit=1)
                filename = invoice_attachment.name
                ir_attachment = invoice_attachment
            else:
                filename = invoice.l10n_it_einvoice_id.display_name
                ir_attachment = invoice.l10n_it_einvoice_id
            zf.writestr(filename, base64.b64decode(ir_attachment['datas']))
            invoice.exported_l10n_it_einvoice_id = True

        zf.close()
        in_memory_zip.seek(0)
        data = in_memory_zip.read()
        return data

    @http.route('/download_zip_fatturepa/<model("account.move"):invoices>', type='http', auth='user')
    def export_zip_invoices(self, invoices, **kwargs):
        """
        This function allows to generate and download an eletronic invoices's zip
        :param invoices: Invoices's RecordSet
        :param kwargs: Dict
        :return: Void
        """
        data = self._generate_zipped_file(invoices)
        zip_name = 'e_invoices_' + str(fields.Datetime.now()) + '.zip'
        return request.make_response(
            data,
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"' % zip_name),
                ('Content-Type', 'application/octet-stream')
            ]
        )
