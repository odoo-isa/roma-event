# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
import re
import base64
from lxml import etree
from asn1crypto import cms
from odoo.exceptions import ValidationError, UserError
from logging import getLogger

_logger = getLogger(__name__)


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    def _create_invoice_from_mail(self, att_content, att_name, from_address):
        if re.search("([A-Z]{2}[A-Za-z0-9]{2,28}_[A-Za-z0-9]{0,5}.xml.p7m)", att_name):
            code_att_content = base64.encodestring(att_content)
            stream_content = base64.decodestring(code_att_content)
            stream_info = cms.ContentInfo.load(stream_content)
            att_content = stream_info['content']['encap_content_info']['content'].native

        if self.env['account.move'].search([('l10n_it_einvoice_name', '=', att_name)], limit=1):
            # invoice already exist
            _logger.info('E-invoice already exist: %s', att_name)
            return

        invoice_attachment = self.env['ir.attachment'].create({
                'name': att_name,
                'datas': base64.encodestring(att_content),
                'type': 'binary',
                'res_model': 'mail.compose.message'
                })

        try:
            tree = etree.fromstring(att_content)
        except Exception:
            raise UserError(_('The xml file is badly formatted : {}').format(att_name))

        invoice = self.env['account.move']._import_xml_invoice(tree)
        invoice.l10n_it_send_state = "new"
        invoice.source_email = from_address
        invoice.message_post(attachment_ids=[invoice_attachment.id])
        self._cr.commit()

        _logger.info('New E-invoice: %s', att_name)
