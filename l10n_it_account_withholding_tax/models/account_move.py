# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_withholding_tax = fields.Boolean(
        string='is withholding account move',
        help='''Technical field that indicate if the move is a withholding tax''',
        readonly=True
    )

    def adding_extra_info(self):
        res = super(AccountMove, self).adding_extra_info()
        # Adding info on withholding tax on xml report of invoice
        withholding_tax_line = self.line_ids.filtered(lambda l: l.mapped("tax_line_id").account_tax_type == 'withholding_tax')
        if withholding_tax_line:
            withholding_tax_ids = self._get_withholding_tax_info(withholding_tax_line)
            res.update(withholding_tax_info=withholding_tax_ids)
        return res

    def _get_withholding_tax_info(self, withholding_tax_line):
        withholding_tax_info = []
        if withholding_tax_line:
            for line in withholding_tax_line:
                info_dict = {
                    'tipo_ritenuta': 'RT01' if self.partner_id.company_type == 'person' else 'RT02',
                    'importo_ritenuta': abs(line.balance),
                    'aliquota_ritenuta': abs(line.tax_line_id.amount),
                    'causale_pagamento': line.tax_line_id.withholding_payment_details if line.tax_line_id.withholding_payment_details else ""
                }
                withholding_tax_info.append(info_dict)
        return withholding_tax_info

    def _add_extra_info(self, body_tree, element, invoice_form, invoice_line_form, message_to_log):
        """
        This method is used for adding extra info for invoice line
        :param body_tree: all xml
        :param element: is "DettaglioLinea"
        :param invoice_form: Form mapping of invoice header
        :param invoice_line_form: Form mapping invoice line
        :param message_to_log: List error to log
        :return:
        """
        res = super(AccountMove, self)._add_extra_info(body_tree, element, invoice_form, invoice_line_form, message_to_log)
        # withholding tax on line is only a flag. The withholding data is on xml header
        withholding_data = body_tree.xpath('.//DatiGeneraliDocumento/DatiRitenuta')
        # Check if line has a whitholding tax
        ritenuta = element.xpath('.//Ritenuta')
        if withholding_data and ritenuta:
            withholding_tax_id = None
            if len(withholding_data) > 1:
                message = _(
                    '''Is not possible to import invoice with multiple withholding tax. Please check the  
                                invoice before importing it. Useful details:<br/>
                    <ul>Invoice Line: %(line_number)s</ul>
                    <ul>Product: %(product)s</ul>
                    <ul>Price Unit: %(price_unit)s</ul>
                    <ul>Quantity: %(quantity)s</ul>''' % {
                        'line_number': invoice_line_form.sequence,
                        'product': invoice_line_form.product_id.name,
                        'price_unit': invoice_line_form.price_unit,
                        'quantity': invoice_line_form.quantity
                    }
                )
                self.activity_schedule('mail.mail_activity_data_warning', note=message, user_id=self.env.user.id)

                _logger.error(_('Is not possible to import invoice with multiple withholding tax. Please check the '
                                'invoice before importing it.'))
                return res
            withholding_data = withholding_data[0]
            payment_details = withholding_data.xpath('.//CausalePagamento')[0].text
            # Search the withholding tax for payment details info
            withholding_tax = self.env['account.tax'].search([
                ('withholding_payment_details', '=', payment_details)
            ])
            # Withholding tax not founded
            if not withholding_tax:
                message_to_log.append("%s<br/>%s" % (
                    _("Unable to find withholding tax, useful informations from XML file:"),
                    self._compose_info_message(body_tree, './/DatiGeneraliDocumento/DatiRitenuta')
                ))
            # Founded more than one withholding tax but exists partner
            elif len(withholding_tax) > 1:
                # Unable to find withholding tax
                message_to_log.append("%s<br/>%s" % (
                    _("Founded more than one withholding tax, useful informations from XML file:"),
                    self._compose_info_message(body_tree, './/DatiGeneraliDocumento/DatiRitenuta')
                ))
            else:
                withholding_tax_id = withholding_tax[0]

            if withholding_tax_id:
                invoice_line_form.tax_ids.add(withholding_tax_id)
        return res

    def _body_extra_info(self, body_tree, invoice_form, message_to_log):
        res = super(AccountMove, self)._body_extra_info(body_tree, invoice_form, message_to_log)
        cassa_previdenziale = body_tree.xpath('.//DatiGeneraliDocumento/DatiCassaPrevidenziale')
        if not cassa_previdenziale:
            return res
        for prev in cassa_previdenziale:
            with invoice_form.invoice_line_ids.new() as invoice_line_form:
                l10n_it_kind_exoneration = prev.xpath('.//Natura')[0].text if prev.xpath('.//Natura') else None
                cassa_prev_id = self.env['account.tax'].search([
                    ('name', '=', prev.xpath('.//TipoCassa')[0].text),
                    ('amount', '=', prev.xpath('.//AlCassa')[0].text),
                    ('account_tax_type', '=', 'cassa_previdenziale')
                ], limit=1)
                if l10n_it_kind_exoneration:
                    tax_id = self.env['account.tax'].search([
                        ('company_id', '=', invoice_form.company_id.id),
                        ('amount_type', '=', 'percent'),
                        ('type_tax_use', '=', 'purchase'),
                        ('amount', '=', prev.xpath('.//AliquotaIVA')[0].text),
                        ('l10n_it_kind_exoneration', '=', l10n_it_kind_exoneration)
                    ], limit=1)
                else:
                    tax_id = self.env['account.tax'].search([
                        ('company_id', '=', invoice_form.company_id.id),
                        ('amount_type', '=', 'percent'),
                        ('type_tax_use', '=', 'purchase'),
                        ('amount', '=', prev.xpath('.//AliquotaIVA')[0].text)
                    ], limit=1)
                invoice_line_form.name = '%s %s - %s' % (prev.xpath('.//TipoCassa')[0].text, cassa_prev_id.tax_group_id.name, prev.xpath('.//AlCassa')[0].text) + '%'
                invoice_line_form.price_unit = float(prev.xpath('.//ImportoContributoCassa')[0].text)
                invoice_line_form.tax_ids.clear()
                if tax_id:
                    invoice_line_form.tax_ids.add(tax_id)
                else:
                    if l10n_it_kind_exoneration:
                        message_to_log.append(_("Tax not found with percentage: %s and exoneration %s for the article: %s") % (prev.xpath('.//AliquotaIVA')[0].text,
                                                                                                                             l10n_it_kind_exoneration,
                                                                                                                             invoice_line_form.name))
                    else:
                        message_to_log.append(_("Tax not found with percentage: %s for the article: %s") % (prev.xpath('.//AliquotaIVA')[0].text,
                                                                                                            invoice_line_form.name))
        return res
