# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import api, models
from odoo.tools.float_utils import float_compare


class L10nItVatReport(models.AbstractModel):
    _name = "l10n_it.vat.report"
    _description = "Italian Vat Report"

    def parent_sezione(self, type_tax_use, type_line):
        """
        Questa funzione ritorna il parent relativo ad una Riga
        :param type_tax_use: String (Sale / Purchase)
        :param type_line: String (base / tax / no_tax)
        :return: Object
        """
        external_type_tax_use = False
        parent = False
        # Se è un'imposta di Tipo Vendite e la linea è "Imponibile", il padre è "I - Vendite"
        if type_line == 'base' and type_tax_use == 'sale':
            external_type_tax_use = 'l10n_it_account_tax_report.tax_report_title_operations_sales'
        # Se è un'imposta di Tipo Acquisti e la linea è "Imponibile", il padre è "II - Acquisti"
        if type_line == 'base' and type_tax_use == 'purchase':
            external_type_tax_use = 'l10n_it_account_tax_report.tax_report_title_operations_purchase'
        # Se è un'imposta di Tipo Vendite e la linea è "Iva", il padre è "IV - Debito"
        if type_line == 'tax' and type_tax_use == 'sale':
            external_type_tax_use = 'l10n_it_account_tax_report.tax_report_title_taxes_debit'
        # Se è un'imposta di Tipo Acquisti e la linea è "Iva indetraibile", il padre è "V - Credito"
        if type_line == 'tax' and type_tax_use == 'purchase':
            external_type_tax_use = 'l10n_it_account_tax_report.tax_report_title_taxes_credit'
        # Se è un'imposta di Tipo Acquisti e la linea è "Iva Indetraibile", il padre è "VI - Indetraibile"
        if type_line == 'no_tax' and type_tax_use == 'purchase':
            external_type_tax_use = 'l10n_it_account_tax_report.tax_report_title_taxes_not_recoverable'
        if external_type_tax_use:
            parent = self.env.ref(external_type_tax_use, False)
        return parent

    def imposta_tag_su_riga(self, line_obj, section_obj, type_tax_use, type_line):
        """
        Questa funzione permette di impostare la tax grid sulla riga di ripartizione in esame
        :param line_obj: Object
        :param section_obj: Object
        :param type_tax_use: String (Sale / Purchase)
        :param type_line: String (fatture / note credito)
        """
        tag_obj = None
        if (type_tax_use == 'sale' and type_line == 'fatture') or (type_tax_use == 'purchase' and type_line == 'note_credito'):
            tag_obj = section_obj.tag_ids.filtered(lambda t: not t.tax_negate)
        elif (type_tax_use == 'sale' and type_line == 'note_credito') or (type_tax_use == 'purchase' and type_line == 'fatture'):
            tag_obj = section_obj.tag_ids.filtered(lambda t: t.tax_negate)
        if tag_obj:
            line_obj.write({
                'tag_ids': [(4, tag_obj.id, 0)]
            })

    def crea_sezione(self, tax_obj, prefix, code, name):
        """
        Genera una Sezione
        :param tax_obj: Object
        :param prefix: String (generate_amount / generate_tax / generate_no_tax)
        :param code: String (0. / 1. / 2.)
        :param name: String (Operazioni su / Iva su / Iva indetraibile su)
        :return: Object
        """
        external_id_section = prefix + tax_obj.description
        code_section = code + tax_obj.description
        name_section = code_section + '. ' + name + tax_obj.name
        complete_external_id = 'l10n_it_account_tax_report.%s' % external_id_section
        section_obj = self.env.ref(complete_external_id, False)
        if not section_obj:
            country_id = self.env.ref('base.it', False)
            # Creo la Sezione (Nota! Impostando il "tag_name" Odoo di base, crea automaticamente i tag)
            section_obj = self.env['account.tax.report.line'].create({
                'name': name_section,
                'code': code_section,
                'tag_name': code_section,
                'country_id': country_id.id if country_id else False,
                'sequence': 1
            })
            # Creo l'identificatore esterno per la Sezione
            self.env['ir.model.data'].create({
                'module': 'l10n_it_account_tax_report',
                'name': external_id_section,
                'model': 'account.tax.report.line',
                'res_id': section_obj.id,
                'noupdate': True
            })
        return section_obj

    def crea_sezione_da_riga(self, tax_report_line_dict, invoice_repartition_line_obj, tax_obj):
        """
        Questa funzione permette, data una linea di ripartizione per fattura, di creare la relativa Sezione
        :param tax_report_line_dict: Dict ({'parent_key': [tax_report_lines]})
        :param invoice_repartition_line_obj: Object
        :param tax_obj: Object
        """
        tag_ids = self.get_module_tags()
        type_tax = tax_obj.type_tax_use
        type_line = invoice_repartition_line_obj.repartition_type
        section_obj = None
        # Imponibile
        if type_line == 'base':
            section_obj = self.crea_sezione(tax_obj, 'generate_amount', '0.', 'Operazioni su ')
            refund_lines_obj = tax_obj.refund_repartition_line_ids.filtered(
                lambda r: r.repartition_type == 'base'
            )
        # Se l'Importo dell'imposta è maggiore di zero, allora possono essere create sezioni per iva / iva indetraibile:
        if type_line == 'tax' and float_compare(tax_obj.amount, 0.0, precision_digits=4) > 0:
            account_obj = invoice_repartition_line_obj.account_id
            # Iva
            if account_obj and account_obj.l10n_it_account_usage == 'tax_account':
                section_obj = self.crea_sezione(tax_obj, 'generate_tax', '1.', 'Iva su ')
                refund_lines_obj = tax_obj.refund_repartition_line_ids.filtered(
                    lambda r: r.repartition_type == 'tax' and r.account_id
                    and r.account_id.l10n_it_account_usage == 'tax_account'
                )
            # Iva Indetraibile
            elif account_obj and not account_obj.l10n_it_account_usage != 'tax_account' and type_tax != 'sale':
                section_obj = self.crea_sezione(tax_obj, 'generate_no_tax', '2.', 'Iva indetraibile su ')
                refund_lines_obj = tax_obj.refund_repartition_line_ids.filtered(
                    lambda r: r.repartition_type == 'tax' and r.account_id
                    and not r.account_id.l10n_it_account_usage != 'tax_account'
                )
            elif not account_obj and type_tax != 'sale':
                section_obj = self.crea_sezione(tax_obj, 'generate_no_tax', '2.', 'Iva indetraibile su ')
                refund_lines_obj = tax_obj.refund_repartition_line_ids.filtered(
                    lambda r: r.repartition_type == 'tax' and not r.account_id
                )
        for tag_obj in invoice_repartition_line_obj.tag_ids:
            if tag_obj.id in tag_ids:
                invoice_repartition_line_obj.write({'tag_ids': [(3, tag_obj.id, 0)]})
        if section_obj:
            if section_obj.code[0] == '2' and type_line == 'tax' and type_tax == 'purchase':
                external_type_tax_use = 'l10n_it_account_tax_report.tax_report_title_taxes_not_recoverable'
                base_parent_tax_obj = self.env.ref(external_type_tax_use, False)
            else:
                base_parent_tax_obj = self.parent_sezione(type_tax, type_line)
            # Per ogni Sezione creata, reperisco il parent e lo aggiungo come chiave al dizionario, in modo da avere:
            # {padre: [sezione1, sezione2,..., sezione i]} e ordino la lista per nome
            if base_parent_tax_obj:
                if base_parent_tax_obj not in tax_report_line_dict.keys():
                    tax_report_line_dict.update({base_parent_tax_obj: [section_obj]})
                elif section_obj not in tax_report_line_dict[base_parent_tax_obj]:
                    tax_report_line_dict[base_parent_tax_obj].append(section_obj)
            # Associo alla Sezione la relativa tax grid
            self.imposta_tag_su_riga(invoice_repartition_line_obj, section_obj, type_tax, 'fatture')
            # Ricerco il tipo della linea di ripartizione fatture tra le righe di ripartizione per note di credito
            for refund_line_obj in refund_lines_obj:
                for refund_tag_obj in refund_line_obj.tag_ids:
                    if refund_tag_obj.id in tag_ids:
                        refund_line_obj.write({'tag_ids': [(3, refund_tag_obj.id, 0)]})
                # Associo alla Sezione la relativa tax grid
                self.imposta_tag_su_riga(refund_line_obj, section_obj, type_tax, 'note_credito')

    @api.model
    def genera_sezioni_da_imposte(self):
        """
        Per ogni imposta filtrata, vengono create le relative Sezioni e Tax Grids
        """
        # Filtro tutte le Imposte che hanno il gruppo d'imposta con le proprietà impostate
        all_account_tax_obj = self.env['account.tax'].search([
            ('tax_group_id.property_tax_payable_account_id', 'not in', []),
            ('tax_group_id.property_tax_receivable_account_id', 'not in', []),
            ('tax_group_id.property_advance_tax_payment_account_id', 'not in', [])
        ])
        tax_report_line_dict = {}
        for account_tax_obj in all_account_tax_obj:
            for invoice_repartition_line_obj in account_tax_obj.invoice_repartition_line_ids:
                self.crea_sezione_da_riga(tax_report_line_dict, invoice_repartition_line_obj, account_tax_obj)
        # Ordino il dizionario per nome
        for parent_obj in tax_report_line_dict:
            values = tax_report_line_dict[parent_obj]
            order_report_line_by_name = sorted(values, key=lambda v: v.name, reverse=False)
            ordered_report_line_ids = []
            sequence = 1
            for ordered_report_line in order_report_line_by_name:
                sequence = sequence + 1
                ordered_report_line.write({'sequence': sequence})
                ordered_report_line_ids.append(ordered_report_line.id)
            parent_obj.write({'children_line_ids': [(6, 0, ordered_report_line_ids)]})

    def get_module_tags(self):
        # Prendo tutte le sezioni create con questo modulo (tranne quelle caricate da xml)
        res = []
        ir_model_data_obj = self.env['ir.model.data'].search([
            ('module', 'like', 'l10n_it_account_tax_report'),
            ('model', 'like', 'account.tax.report.line'),
            ('name', 'like', '%generate_%')
        ])
        if ir_model_data_obj:
            all_sections_ids = ir_model_data_obj.mapped('res_id')
            all_sections_obj = self.env['account.tax.report.line'].browse(all_sections_ids)
            for section_obj in all_sections_obj:
                res.extend(section_obj.tag_ids.ids)
        res = set(res)
        return res
