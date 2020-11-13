# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tests.common import Form
from odoo.tools import float_repr
from odoo.modules import get_module_resource
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import base64
import re
import lxml.etree as ET
from io import BytesIO
from logging import getLogger
from asn1crypto import cms
from lxml import etree

_logger = getLogger(__name__)

DEFAULT_FACTUR_ITALIAN_DATE_FORMAT = '%Y-%m-%d'

class SdiException(Exception):
    pass

class AccountMove(models.Model):
    _inherit = 'account.move'

    related_document_ids = fields.One2many(
        string='Related Documents',
        required=False,
        readonly=False,
        comodel_name='l10n_it_edi.related_document',
        inverse_name='move_id',
        help="Represent related document associated to the move",
        copy=False
    )

    create_and_send_einvoices_in_separate_steps = fields.Boolean(
        string='create_and_send_einvoices_in_separate_steps',
        help='Functional Fields',
        copy=False,
        compute='_get_configuration_on_e_invoice'
    )

    l10n_it_edi_preview_link = fields.Char(
        string="Preview link",
        readonly=True,
        compute="_compute_xml_preview_link"
    )

    rounding_on_document = fields.Float(
        string='Rounding on Document',
        required=False,
        readonly=True,
        help='Rounding on Document',
        copy=False,
    )

    l10n_it_total_amount = fields.Float(
        string='Total Invoice Amount',
        help='Value of the total amount coming from SDI',
    )

    is_equal_amount = fields.Boolean(
        string='Is equal amount',
        compute='_compute_equal_amount',
        default=False,
        help='True if value of the total amount of invoice is different of total amount coming from SDI',
    )

    @api.depends('amount_total', 'l10n_it_total_amount')
    def _compute_equal_amount(self):
        for record in self:
            record.is_equal_amount = False
            if not record.l10n_it_total_amount in [None, False, 0.0]:
                if record.l10n_it_total_amount != round(record.amount_total, 2):
                    record.is_equal_amount = True

    def _check_before_xml_exporting(self):
        seller = self.company_id
        buyer = self.commercial_partner_id

        # <1.1.1.1>
        if not seller.country_id:
            raise UserError(_("%s must have a country") % (seller.display_name))

        # <1.1.1.2>
        if not seller.vat:
            raise UserError(_("%s must have a VAT number") % (seller.display_name))
        elif len(seller.vat) > 30:
            raise UserError(_("The maximum length for VAT number is 30. %s have a VAT number too long: %s.") % (
            seller.display_name, seller.vat))

        # <1.2.1.2>
        if not seller.l10n_it_codice_fiscale:
            raise UserError(_("%s must have a codice fiscale number") % (seller.display_name))

        # <1.2.1.8>
        if not seller.l10n_it_tax_system:
            raise UserError(_("The seller's company must have a tax system."))

        # <1.2.2>
        if not seller.street and not seller.street2:
            raise UserError(_("%s must have a street.") % (seller.display_name))
        if not seller.zip:
            raise UserError(_("%s must have a post code.") % (seller.display_name))
        if len(seller.zip) != 5 and seller.country_id.code == 'IT':
            raise UserError(_("%s must have a post code of length 5.") % (seller.display_name))
        if not seller.city:
            raise UserError(_("%s must have a city.") % (seller.display_name))
        if not seller.country_id:
            raise UserError(_("%s must have a country.") % (seller.display_name))

        # <1.4.1>
        if not buyer.vat and not buyer.l10n_it_codice_fiscale and buyer.country_id.code == 'IT':
            raise UserError(
                _("The buyer, %s, or his company must have either a VAT number either a tax code (Codice Fiscale).") % (
                    buyer.display_name))

        # <1.4.2>
        if not buyer.street and not buyer.street2:
            raise UserError(_("%s must have a street.") % (buyer.display_name))
        if not buyer.zip:
            raise UserError(_("%s must have a post code.") % (buyer.display_name))
        if len(buyer.zip) != 5 and buyer.country_id.code == 'IT':
            raise UserError(_("%s must have a post code of length 5.") % (buyer.display_name))
        if not buyer.city:
            raise UserError(_("%s must have a city.") % (buyer.display_name))
        if not buyer.country_id:
            raise UserError(_("%s must have a country.") % (buyer.display_name))

        for tax_line in self.line_ids.filtered(lambda line: line.tax_line_id):
            if not tax_line.tax_line_id.l10n_it_has_exoneration and tax_line.tax_line_id.amount == 0:
                raise ValidationError(_("%s has an amount of 0.0, you must indicate the kind of exoneration." % tax_line.name))

        if not self.commercial_partner_id.state_id:
            raise UserError(_("%s must have a province.") % (self.commercial_partner_id.display_name))

    def _compute_xml_preview_link(self):
        for record in self:
            record.l10n_it_edi_preview_link = '/l10n_it_edi/preview/%s' % record.id

    def get_fattura_elettronica_preview(self, attachment_id):
        xsl_path = get_module_resource(
            'l10n_it_edi_extension_isa', 'data',
            self.env.user.company_id.l10n_it_edi_preview_style)
        xslt = ET.parse(xsl_path)
        xml_string = attachment_id.get_xml_string()
        xml_file = BytesIO(xml_string)
        recovering_parser = ET.XMLParser(recover=True)
        dom = ET.parse(xml_file, parser=recovering_parser)
        transform = ET.XSLT(xslt)
        newdom = transform(dom)
        return ET.tostring(newdom, pretty_print=True)
    

    def _get_configuration_on_e_invoice(self):
        for record in self:
            record.create_and_send_einvoices_in_separate_steps = self.env.user.company_id.create_and_send_einvoices_in_separate_steps

    def send_pec_mail(self):
        '''
        Inherited the function for sending the electronic invoice for pec: if it has been set in the configuration of
        Create and Send the xml file in separate steps, only the xml will be generated when the invoice is confirmed and
        then, through a button, it will be possible to send the invoice for PEC. If, on the other hand, separate
        management has not been specified in the configuration, the xml file will be generated and sent via pec when the
        invoice is confirmed. When sending the invoice for pec is done using the Send E-invoice button a key is added
        in the context to force the sending (key send_pec_mail).
        '''
        if not self.env.user.company_id.create_and_send_einvoices_in_separate_steps:
            for record in self:
                record.l10n_it_send_state = 'invalid'
            return super(AccountMove, self).send_pec_mail()
        if 'send_pec_mail' in self.env.context:
            return super(AccountMove, self).send_pec_mail()

    def _export_as_xml(self):
        ''' Create the xml file content.
        :return: The XML content as str.
        '''
        self.ensure_one()

        def format_date(dt):
            # Format the date in the italian standard.
            dt = dt or datetime.now()
            return dt.strftime(DEFAULT_FACTUR_ITALIAN_DATE_FORMAT)

        def format_monetary(number, currency):
            # Format the monetary values to avoid trailing decimals (e.g. 90.85000000000001).
            return float_repr(number, min(2, currency.decimal_places))

        def format_numbers(number):
            #format number to str with between 2 and 8 decimals (event if it's .00)
            number_splited = str(number).split('.')
            if len(number_splited) == 1:
                return "%.02f" % number

            cents = number_splited[1]
            if len(cents) > 8:
                return "%.08f" % number
            return float_repr(number, max(2, len(cents)))

        def format_numbers_two(number):
            #format number to str with 2 (event if it's .00)
            return "%.02f" % number

        def discount_type(discount):
            return 'SC' if discount > 0 else 'MG'

        def format_phone(number):
            if not number:
                return False
            number = number.replace(' ', '').replace('/', '').replace('.', '')
            if len(number) > 4 and len(number) < 13:
                return number
            return False

        def get_vat_number(vat):
            return vat[2:].replace(' ', '')

        def get_vat_country(vat):
            return vat[:2].upper()

        def in_eu(partner):
            europe = self.env.ref('base.europe', raise_if_not_found=False)
            country = partner.country_id
            if not europe or not country or country in europe.country_ids:
                return True
            return False

        formato_trasmissione = "FPR12"
        if len(self.commercial_partner_id.l10n_it_pa_index or '1') == 6:
            formato_trasmissione = "FPA12"

        if self.type == 'out_invoice':
            document_type = 'TD01'
        elif self.type == 'out_refund':
            document_type = 'TD04'
        else:
            document_type = 'TD0X'

        pdf = self.env.ref('account.account_invoices').render_qweb_pdf(self.id)[0]
        pdf = base64.b64encode(pdf)
        pdf_name = re.sub(r'\W+', '', self.name) + '.pdf'

        # Create file content.
        template_values = {
            'record': self,
            'format_date': format_date,
            'format_monetary': format_monetary,
            'format_numbers': format_numbers,
            'format_numbers_two': format_numbers_two,
            'format_phone': format_phone,
            'discount_type': discount_type,
            'get_vat_number': get_vat_number,
            'get_vat_country': get_vat_country,
            'in_eu': in_eu,
            'abs': abs,
            'formato_trasmissione': formato_trasmissione,
            'document_type': document_type,
            'pdf': pdf,
            'pdf_name': pdf_name,
        }

        extra_info = self.adding_extra_info()
        template_values.update(extra_info)
        content = self.env.ref('l10n_it_edi.account_invoice_it_FatturaPA_export').render(template_values)
        return content

    def _set_id_codice(self):
        """
        This method is used to set idCode in tag "idTrasmittente"
        :return: String
        """
        idCodice = self.company_id.vat
        return idCodice[2:]

    def ddt_reference(self):
        '''
        This function retrive related documents of invoice wich have type ddt and reference of ddt's invoice
        :return: filtered related document of header invoice
        '''
        related_document_obj = list(self.mapped('related_document_ids').filtered(lambda d: d.document_type == 'ddt'))
        return related_document_obj

    def get_fatturapa_art73(self):
        return 'SI' if self.company_id.fatturapa_art73 else ''

    def adding_extra_info(self):
        """
        Method to add extra info on xml report of the invoice.
        """
        progressivo_invio = self.l10n_it_einvoice_name.split("_")[1][:5]
        res = {
            'id_codice': self._set_id_codice(),
            'progressivo_invio': progressivo_invio,
            'fatturapa_art73': self.get_fatturapa_art73(),
            'type_ddt_for_invoice': self.ddt_reference(),
        }
        return res

    def generate_zip_einvoice(self):
        """
        This function check is are generated all xml files for e-invoices
        :return: Action
        """
        # Invoices that don't have xml file
        for invoice in self:
            if invoice.type == 'in_invoice' or invoice.type == 'in_refund':
                if not invoice.l10n_it_einvoice_name:
                    raise UserError(_("Xml File isn't present for invoice with number: %s") % invoice.name)
                # Check if exists attachment for invoice
                invoice_attachment = invoice.env['ir.attachment'].search([
                    ('res_model', 'like', 'account.move'),
                    ('res_id', '=', invoice.id),
                    ('name', 'like', invoice.l10n_it_einvoice_name)
                ], limit=1)
                if not invoice_attachment:
                    raise UserError(_("Attachment File isn't present for invoice with number: %s") % invoice.name)
            else:
                if not invoice.l10n_it_einvoice_id:
                    raise UserError(_("Xml File isn't present for invoice with number: %s") % invoice.name)

        return {
            "type": "ir.actions.act_url",
            "url": "/download_zip_fatturepa/""%s" % ",".join(map(str, self.ids)),
            "target": "new"
        }

    def _create_invoice_from_attachment(self, attachment):
        super(AccountMove, self.with_context(attachment_name=attachment.display_name))._create_invoice_from_attachment(attachment)
        if attachment.mimetype in ('application/octet-stream', 'application/pkcs7-mime'):
            for move in self:
                if re.search("([A-Z]{2}[A-Za-z0-9]{2,28}_[A-Za-z0-9]{0,5}.xml.p7m)", attachment.name):
                    attachment.mimetype = 'application/pkcs7-mime'
                stream_content = base64.decodestring(attachment.datas)
                stream_info = cms.ContentInfo.load(stream_content)
                xml_data = stream_info['content']['encap_content_info']['content'].native
                move.with_context(attachment_name=attachment.display_name)._import_xml_invoice(etree.fromstring(xml_data))

    def _import_xml_invoice(self, tree):
        ''' Extract invoice values from the E-Invoice xml tree passed as parameter.

                :param content: The tree of the xml file.
                :return: A dictionary containing account.invoice values to create/update it.
                '''

        invoices = self.env['account.move']
        multi = False

        # possible to hav
        # e multiple invoices in the case of an invoice batch, the batch itself is repeated for every invoice of the batch
        for body_tree in tree.xpath('//FatturaElettronicaBody'):
            if multi:
                # make sure all the iterations create a new invoice record (except the first which could have already created one)
                self = self.env['account.move']
            multi = True

            # type must be present in the context to get the right behavior of the _default_journal method (account.move).
            # journal_id must be present in the context to get the right behavior of the _default_account method (account.move.line).

            elements = tree.xpath('//CessionarioCommittente//IdCodice')
            company = elements and self.env['res.company'].search([('vat', 'ilike', elements[0].text)], limit=1)
            if not company:
                elements = tree.xpath('//CessionarioCommittente//CodiceFiscale')
                company = elements and self.env['res.company'].search(
                    [('l10n_it_codice_fiscale', 'ilike', elements[0].text)], limit=1)

            if company:
                self_ctx = self_ctx.with_context(company_id=company.id)
            else:
                company = self.env.company
                if elements:
                    _logger.info(
                        _('Company not found with codice fiscale: %s. The company\'s user is set by default.') %
                        elements[0].text)
                else:
                    _logger.info(_('Company not found. The company\'s user is set by default.'))

            if not self.env.is_superuser():
                if self.env.company != company:
                    raise UserError(_(
                        "You can only import invoice concern your current company: %s") % self.env.company.display_name)

            # Refund type.
            # TD01 == invoice
            # TD02 == advance/down payment on invoice
            # TD03 == advance/down payment on fee
            # TD04 == credit note
            # TD05 == debit note
            # TD06 == fee
            elements = tree.xpath('//DatiGeneraliDocumento/TipoDocumento')
            if elements and elements[0].text and elements[0].text in ('TD01', 'TD02', 'TD03', 'TD05', 'TD06', 'TD07'):
                type = 'in_invoice'
            else:
                type = 'in_refund'
            self_ctx = self.with_context(default_type=type)
            # self could be a single record (editing) or be empty (new).
            self_ctx = self_ctx.with_context(check_move_validity=False)
            with Form(self_ctx, view='l10n_it_edi_extension_isa.account_move_form_for_import_xml') as invoice_form:
                message_to_log = []

                # Partner (first step to avoid warning 'Warning! You must first select a partner.'). <1.2>
                elements = tree.xpath('//CedentePrestatore//IdCodice')
                partner = elements and self.env['res.partner'].search(
                    ['&', ('vat', 'ilike', elements[0].text), '|', ('company_id', '=', company.id),
                     ('company_id', '=', False)], limit=1)
                if not partner:
                    elements = tree.xpath('//CedentePrestatore//CodiceFiscale')
                    partner = elements and self.env['res.partner'].search(
                        ['&', ('l10n_it_codice_fiscale', '=', elements[0].text), '|', ('company_id', '=', company.id),
                         ('company_id', '=', False)], limit=1)
                if not partner:
                    elements = tree.xpath('//DatiTrasmissione//Email')
                    partner = elements and self.env['res.partner'].search(
                        ['&', '|', ('email', '=', elements[0].text), ('l10n_it_pec_email', '=', elements[0].text), '|',
                         ('company_id', '=', company.id), ('company_id', '=', False)], limit=1)
                if partner:
                    invoice_form.partner_id = partner
                else:
                    message_to_log.append("%s<br/>%s" % (
                        _("Vendor not found, useful informations from XML file:"),
                        self._compose_info_message(
                            tree, './/CedentePrestatore')))

                # Numbering attributed by the transmitter. <1.1.2>
                elements = tree.xpath('//ProgressivoInvio')
                if elements:
                    invoice_form.invoice_payment_ref = elements[0].text

                elements = body_tree.xpath('.//DatiGeneraliDocumento//Numero')
                if elements:
                    invoice_form.ref = elements[0].text

                # Currency. <2.1.1.2>
                elements = body_tree.xpath('.//DatiGeneraliDocumento/Divisa')
                if elements:
                    currency_str = elements[0].text
                    currency = self.env.ref('base.%s' % currency_str.upper(), raise_if_not_found=False)
                    if currency != self.env.company.currency_id and currency.active:
                        invoice_form.currency_id = currency

                # Date. <2.1.1.3>
                elements = body_tree.xpath('.//DatiGeneraliDocumento/Data')
                if elements:
                    date_str = elements[0].text
                    date_obj = datetime.strptime(date_str, DEFAULT_FACTUR_ITALIAN_DATE_FORMAT)
                    invoice_form.invoice_date = date_obj.strftime(DEFAULT_FACTUR_ITALIAN_DATE_FORMAT)

                #  Dati Bollo. <2.1.1.6>
                elements = body_tree.xpath('.//DatiGeneraliDocumento/DatiBollo/ImportoBollo')
                if elements:
                    invoice_form.l10n_it_stamp_duty = float(elements[0].text)

                # List of all amount discount (will be add after all article to avoid to have a negative sum)
                discount_list = []
                percentage_global_discount = 1.0

                # Global discount. <2.1.1.8>
                discount_elements = body_tree.xpath('.//DatiGeneraliDocumento/ScontoMaggiorazione')
                total_discount_amount = 0.0
                if discount_elements:
                    for discount_element in discount_elements:
                        discount_line = discount_element.xpath('.//Tipo')
                        discount_sign = -1
                        if discount_line and discount_line[0].text == 'SC':
                            discount_sign = 1
                        discount_percentage = discount_element.xpath('.//Percentuale')
                        if discount_percentage and discount_percentage[0].text:
                            percentage_global_discount *= 1 - float(discount_percentage[0].text) / 100 * discount_sign

                        discount_amount_text = discount_element.xpath('.//Importo')
                        if discount_amount_text and discount_amount_text[0].text:
                            discount_amount = float(discount_amount_text[0].text) * discount_sign * -1
                            discount = {}
                            discount["seq"] = 0

                            if discount_amount < 0:
                                discount["name"] = _('GLOBAL DISCOUNT')
                            else:
                                discount["name"] = _('GLOBAL EXTRA CHARGE')
                            discount["amount"] = discount_amount
                            discount["tax"] = []
                            discount_list.append(discount)

                # Total Amount
                sign_credit_note = +1
                total_document_amount = body_tree.xpath('.//DatiGeneraliDocumento/ImportoTotaleDocumento')
                if total_document_amount and total_document_amount[0].text:
                    invoice_form.l10n_it_total_amount = float(total_document_amount[0].text)
                    if float(total_document_amount[0].text) < 0:
                        sign_credit_note = -1

                # Rounding
                rounding = body_tree.xpath('.//DatiGeneraliDocumento/Arrotondamento')
                if rounding:
                    rounding = float(rounding[0].text)

                # Comment. <2.1.1.11>
                elements = body_tree.xpath('.//DatiGeneraliDocumento//Causale')
                for element in elements:
                    invoice_form.narration = '%s%s\n' % (invoice_form.narration or '', element.text)

                # Informations relative to the purchase order, the contract, the agreement,
                # the reception phase or invoices previously transmitted
                # <2.1.2> - <2.1.6>
                for document_type in ['DatiOrdineAcquisto', 'DatiContratto', 'DatiConvenzione', 'DatiRicezione',
                                      'DatiFattureCollegate']:
                    elements = body_tree.xpath('.//DatiGenerali/' + document_type)
                    if elements:
                        for element in elements:
                            message_to_log.append("%s %s<br/>%s" % (document_type, _("from XML file:"),
                                                                    self._compose_info_message(element, '.')))
                            element_ref_row = element.xpath('RiferimentoNumeroLinea')
                            if not element_ref_row:
                                with invoice_form.related_document_ids.new() as related_document_form:
                                    related_document_form.name = element.xpath('IdDocumento')[0].text
                                    related_document_form.date = element.xpath('Data')[0].text if element.xpath('Data') else False
                                    related_document_form.code = element.xpath('CodiceCommessaConvenzione')[0].text if element.xpath('CodiceCommessaConvenzione') else ''
                                    if element.tag == 'DatiOrdineAcquisto':
                                        related_document_form.document_type = 'order'
                                    elif element.tag == 'DatiContratto':
                                        related_document_form.document_type = 'contract'
                                    elif element.tag == 'DatiConvenzione':
                                        related_document_form.document_type = 'agreement'
                                    elif element.tag == 'DatiRicezione':
                                        related_document_form.document_type = 'reception'
                                    elif element.tag == 'DatiFattureCollegate':
                                        related_document_form.document_type = 'invoice'

                #  Dati DDT. <2.1.8>
                elements = body_tree.xpath('.//DatiGenerali/DatiDDT')
                if elements:
                    message_to_log.append("%s<br/>%s" % (
                        _("Transport informations from XML file:"),
                        self._compose_info_message(body_tree, './/DatiGenerali/DatiDDT')))
                    for element in elements:
                        element_ref_row = element.xpath('RiferimentoNumeroLinea')
                        if not element_ref_row:
                            with invoice_form.related_document_ids.new() as related_document_form:
                                related_document_form.name = element.xpath('NumeroDDT')[0].text
                                related_document_form.date = element.xpath('DataDDT')[0].text if element.xpath('Data') else None
                                related_document_form.document_type = 'ddt'

                # Due date. <2.4.2.5>
                elements = body_tree.xpath('.//DatiPagamento/DettaglioPagamento/DataScadenzaPagamento')
                if elements:
                    date_str = elements[0].text
                    date_obj = datetime.strptime(date_str, DEFAULT_FACTUR_ITALIAN_DATE_FORMAT)
                    invoice_form.invoice_date_due = fields.Date.to_string(date_obj)

                # Total amount. <2.4.2.6>
                elements = body_tree.xpath('.//ImportoPagamento')
                amount_total_import = 0
                for element in elements:
                    amount_total_import += float(element.text)
                if amount_total_import:
                    message_to_log.append(_("Total amount from the XML File: %s") % (
                        amount_total_import))

                # Bank account. <2.4.2.13>
                if invoice_form.type not in ('out_invoice', 'in_refund'):
                    elements = body_tree.xpath('.//DatiPagamento/DettaglioPagamento/IBAN')
                    if elements:
                        if invoice_form.partner_id and invoice_form.partner_id.commercial_partner_id:
                            bank = self.env['res.partner.bank'].search([
                                ('acc_number', '=', elements[0].text),
                                ('partner_id.id', '=', invoice_form.partner_id.commercial_partner_id.id)
                            ])
                        else:
                            bank = self.env['res.partner.bank'].search([('acc_number', '=', elements[0].text)])
                        if bank:
                            invoice_form.invoice_partner_bank_id = bank
                        else:
                            message_to_log.append("%s<br/>%s" % (
                                _("Bank account not found, useful informations from XML file:"),
                                self._compose_multi_info_message(
                                    body_tree, ['.//DatiPagamento//Beneficiario',
                                                './/DatiPagamento//IstitutoFinanziario',
                                                './/DatiPagamento//IBAN',
                                                './/DatiPagamento//ABI',
                                                './/DatiPagamento//CAB',
                                                './/DatiPagamento//BIC',
                                                './/DatiPagamento//ModalitaPagamento'])))
                    else:
                        elements = body_tree.xpath('.//DatiPagamento/DettaglioPagamento')
                        if elements:
                            message_to_log.append("%s<br/>%s" % (
                                _("Bank account not found, useful informations from XML file:"),
                                self._compose_info_message(body_tree, './/DatiPagamento')))

                # Other header info
                self._body_extra_info(body_tree, invoice_form, message_to_log)

                # Invoice lines. <2.2.1>
                elements = body_tree.xpath('.//DettaglioLinee')
                if elements:
                    for element in elements:
                        with invoice_form.invoice_line_ids.new() as invoice_line_form:

                            # Sequence.
                            line_elements = element.xpath('.//NumeroLinea')
                            if line_elements:
                                invoice_line_form.sequence = int(line_elements[0].text)

                            # Product.
                            line_elements = element.xpath('.//Descrizione')
                            if line_elements:
                                invoice_line_form.name = " ".join(line_elements[0].text.split())

                            elements_code = element.xpath('.//CodiceArticolo')
                            if elements_code:
                                for element_code in elements_code:
                                    type_code = element_code.xpath('.//CodiceTipo')[0]
                                    code = element_code.xpath('.//CodiceValore')[0]
                                    if type_code.text == 'EAN':
                                        product = self.env['product.product'].search([('barcode', '=', code.text)])
                                        if product:
                                            invoice_line_form.product_id = product
                                            break
                                    if partner:
                                        product_supplier = self.env['product.supplierinfo'].search(
                                            [('name', '=', partner.id), ('product_code', '=', code.text)])
                                        if product_supplier and product_supplier.product_id:
                                            invoice_line_form.product_id = product_supplier.product_id
                                            break
                                if not invoice_line_form.product_id:
                                    for element_code in elements_code:
                                        code = element_code.xpath('.//CodiceValore')[0]
                                        product = self.env['product.product'].search([('default_code', '=', code.text)])
                                        if product:
                                            invoice_line_form.product_id = product
                                            break

                            # Price Unit.
                            line_elements = element.xpath('.//PrezzoUnitario')
                            if line_elements:
                                invoice_line_form.price_unit = float(line_elements[0].text) * sign_credit_note

                            # Quantity.
                            line_elements = element.xpath('.//Quantita')
                            if line_elements:
                                invoice_line_form.quantity = float(line_elements[0].text)
                            else:
                                invoice_line_form.quantity = 1

                            # Taxes
                            tax_element = element.xpath('.//AliquotaIVA')
                            natura_element = element.xpath('.//Natura')
                            invoice_line_form.tax_ids.clear()
                            if tax_element and tax_element[0].text:
                                percentage = float(tax_element[0].text)
                                if natura_element and natura_element[0].text:
                                    l10n_it_kind_exoneration = natura_element[0].text
                                    tax = self.env['account.tax'].search([
                                        ('company_id', '=', invoice_form.company_id.id),
                                        ('amount_type', '=', 'percent'),
                                        ('type_tax_use', '=', 'purchase'),
                                        ('amount', '=', percentage),
                                        ('l10n_it_kind_exoneration', '=', l10n_it_kind_exoneration),
                                    ], limit=1)
                                else:
                                    tax = self.env['account.tax'].search([
                                        ('company_id', '=', invoice_form.company_id.id),
                                        ('amount_type', '=', 'percent'),
                                        ('type_tax_use', '=', 'purchase'),
                                        ('amount', '=', percentage),
                                    ], limit=1)
                                    l10n_it_kind_exoneration = ''

                                if tax:
                                    invoice_line_form.tax_ids.add(tax)
                                else:
                                    if l10n_it_kind_exoneration:
                                        message_to_log.append(_(
                                            "Tax not found with percentage: %s and exoneration %s for the article: %s") % (
                                                                  percentage,
                                                                  l10n_it_kind_exoneration,
                                                                  invoice_line_form.name))
                                    else:
                                        message_to_log.append(
                                            _("Tax not found with percentage: %s for the article: %s") % (
                                                percentage,
                                                invoice_line_form.name))

                            # Discount in cascade mode.
                            # if 3 discounts : -10% -50€ -20%
                            # the result must be : (((price -10%)-50€) -20%)
                            # Generic form : (((price -P1%)-A1€) -P2%)
                            # It will be split in two parts: fix amount and pourcent amount
                            # example: (((((price - A1€) -P2%) -A3€) -A4€) -P5€)
                            # pourcent: 1-(1-P2)*(1-P5)
                            # fix amount: A1*(1-P2)*(1-P5)+A3*(1-P5)+A4*(1-P5) (we must take account of all
                            # percentage present after the fix amount)
                            line_elements = element.xpath('.//ScontoMaggiorazione')
                            total_discount_amount = 0.0
                            total_discount_percentage = percentage_global_discount
                            if line_elements:
                                for line_element in line_elements:
                                    discount_line = line_element.xpath('.//Tipo')
                                    discount_sign = -1
                                    if discount_line and discount_line[0].text == 'SC':
                                        discount_sign = 1
                                    discount_percentage = line_element.xpath('.//Percentuale')
                                    if discount_percentage and discount_percentage[0].text:
                                        pourcentage_actual = 1 - float(
                                            discount_percentage[0].text) / 100 * discount_sign
                                        total_discount_percentage *= pourcentage_actual
                                        total_discount_amount *= pourcentage_actual

                                    discount_amount = line_element.xpath('.//Importo')
                                    if discount_amount and discount_amount[0].text:
                                        total_discount_amount += float(discount_amount[0].text) * discount_sign * -1

                                # Save amount discount.
                                if total_discount_amount != 0:
                                    discount = {}
                                    discount["seq"] = invoice_line_form.sequence + 1

                                    if total_discount_amount < 0:
                                        discount["name"] = _('DISCOUNT: ') + invoice_line_form.name
                                    else:
                                        discount["name"] = _('EXTRA CHARGE: ') + invoice_line_form.name
                                    discount["amount"] = total_discount_amount
                                    discount["tax"] = []
                                    for tax in invoice_line_form.tax_ids:
                                        discount["tax"].append(tax)
                                    discount_list.append(discount)
                            invoice_line_form.discount = (1 - total_discount_percentage) * 100

                            self._add_extra_info(body_tree, element, invoice_form, invoice_line_form, message_to_log)

                # Apply amount discount.
                for discount in discount_list:
                    with invoice_form.invoice_line_ids.new() as invoice_line_form_discount:
                        invoice_line_form_discount.tax_ids.clear()
                        invoice_line_form_discount.sequence = discount["seq"]
                        invoice_line_form_discount.name = discount["name"]
                        invoice_line_form_discount.price_unit = discount["amount"]

            new_invoice = invoice_form.save()
            new_invoice.type = type
            new_invoice.l10n_it_send_state = "other"
            new_invoice.rounding_on_document = rounding

            # discount1 is field introduce by sale_pricelist_multipl_discount
            if hasattr(invoice_line_form._model, 'discount1'):
                for line_discount in new_invoice.line_ids:
                    if line_discount.discount:
                        line_discount.discount1 = line_discount.discount

            # Informations relative to the purchase order, the contract, the agreement,
            # the reception phase or invoices previously transmitted
            # <2.1.2> - <2.1.6>
            for document_type in ['DatiOrdineAcquisto', 'DatiContratto', 'DatiConvenzione',
                                  'DatiRicezione',
                                  'DatiFattureCollegate']:
                elements = body_tree.xpath('.//DatiGenerali/' + document_type)
                if elements:
                    for element in elements:
                        element_ref_row = element.xpath('RiferimentoNumeroLinea')
                        if element_ref_row:
                            invoice_line = new_invoice.invoice_line_ids.filtered(lambda l: l.sequence == int(element_ref_row[0].text))
                            if invoice_line:
                                if element.tag == 'DatiOrdineAcquisto':
                                    document_type = 'order'
                                elif element.tag == 'DatiContratto':
                                    document_type = 'contract'
                                elif element.tag == 'DatiConvenzione':
                                    document_type = 'agreement'
                                elif element.tag == 'DatiRicezione':
                                    document_type = 'reception'
                                elif element.tag == 'DatiFattureCollegate':
                                    document_type = 'invoice'
                                vals = {
                                    'name': element.xpath('IdDocumento')[0].text,
                                    'date':  element.xpath('Data')[0].text if element.xpath('Data') else None,
                                    'code': element.xpath('CodiceCommessaConvenzione')[0].text if element.xpath('CodiceCommessaConvenzione') else '',
                                    'document_type': document_type,
                                    'num_item': element.xpath('NumItem')[0].text if element.xpath('NumItem') else 0
                                }
                                invoice_line.related_document_line_ids = [(0, False, vals)]

            #  Dati DDT. <2.1.8>
            elements = body_tree.xpath('.//DatiGenerali/DatiDDT')
            if elements:
                for element in elements:
                    element_ref_row = element.xpath('RiferimentoNumeroLinea')
                    invoice_line = new_invoice.invoice_line_ids.filtered(
                        lambda l: l.sequence == int(element_ref_row[0].text))
                    if invoice_line:
                        vals = {
                            'name': element.xpath('NumeroDDT')[0].text,
                            'date': element.xpath('DataDDT')[
                                0].text if element.xpath('Data') else None,
                            'document_type': 'ddt'
                        }
                        invoice_line.related_document_line_ids = [(0, False, vals)]

            elements = body_tree.xpath('.//Allegati')
            if elements:
                for element in elements:
                    name_attachment = element.xpath('.//NomeAttachment')[0].text
                    if element.xpath('.//Attachment') and element.xpath('.//Attachment')[0].text:
                        attachment_64 = str.encode(element.xpath('.//Attachment')[0].text)
                        attachment_64 = self.env['ir.attachment'].create({
                            'name': name_attachment,
                            'datas': attachment_64,
                            'type': 'binary',
                        })

                        # default_res_id is had to context to avoid facturx to import his content
                        # no_new_invoice to prevent from looping on the message_post that would create a new invoice without it
                        new_invoice.with_context(no_new_invoice=True, default_res_id=new_invoice.id).message_post(
                            body=(_("Attachment from XML")),
                            attachment_ids=[attachment_64.id]
                        )

            for message in message_to_log:
                new_invoice.message_post(body=message)
            
            if 'attachment_name' in self._context:
                new_invoice.l10n_it_einvoice_name = self.env.context['attachment_name']

            invoices += new_invoice
        return invoices

    def _body_extra_info(self, body_tree, invoice_form, message_to_log):
        """
        Extendable function to add extra info to the header of the invoice.
        :param body_tree: the xml referred to <FatturaElettronicaBody> tag
        :param invoice_form: the form object to fill
        :return: True
        """
        return True

    def _add_extra_info(self, body_tree, element, invoice_form, invoice_line_form, message_to_log):
        """

        :param body_tree:
        :param element:
        :param invoice_line_form:
        :param message_to_log:
        :return:
        """
        return True

    @api.depends('rounding_on_document')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for record in self:
            if record.rounding_on_document:
                record.amount_total += record.rounding_on_document
                record.amount_total_signed += record.rounding_on_document
                record.amount_total_company_signed += record.rounding_on_document
        return res