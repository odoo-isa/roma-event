# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from io import StringIO
import base64
import datetime


from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.tools import float_round
from odoo.tools import format_date

from odoo.addons.http_routing.models.ir_http import slugify

from logging import getLogger

_logger = getLogger(__name__)


class L10nItbankPaperSlip(models.Model):
    _name = "l10n_it.bank_paper.slip"
    _inherit = 'mail.thread'
    _description = "Bank paper slip"

    name = fields.Char(
        string='Name',
        copy=True
    )

    bank_paper_slip_type_id = fields.Many2one(
        string='Bank Paper Slip Type',
        readonly=True,
        comodel_name='l10n_it.bank_paper.slip.types',
        help="Configuration bank paper slip",
        required=True,
        copy=True
    )

    total_amount = fields.Float(
        string='Total Amount',
        required=False,
        readonly=True,
        index=False,
        default=0.0,
        copy=True
    )

    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('sent', 'Sent'), ('accepted', 'Accepted'), ('credited', 'Credited')],
        track_visibility='onchange',
        copy=True
    )

    bank_paper_ids = fields.One2many(
        string='Bank Paper',
        comodel_name='l10n_it.bank_paper',
        inverse_name='bank_paper_id',
        help="Bank papers linked to bank paper slip",
        copy=True
    )

    acceptance_date = fields.Date(
        string='Acceptance date',
        copy=True
    )

    acceptance_account_move_ids = fields.One2many(
        string='Acceptance Account Move',
        comodel_name='account.move.line',
        inverse_name='bank_paper_slip_id',
        copy=False
    )

    release_date = fields.Date(
        string='Release Date',
        copy=True
    )

    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        compute="_get_bank_paper_info",
        store=True,
        copy=True
    )

    currency_id = fields.Many2one(
        string='Currency',
        compute="_get_bank_paper_info",
        store=True,
        comodel_name='res.currency',
        copy=True
    )

    company_currency_id = fields.Many2one(
        string='Company Currency',
        compute="_get_bank_paper_info",
        store=True,
        comodel_name='res.currency',
        copy=True
    )

    credit_move_id = fields.Many2one(
        string='Credit Move',
        comodel_name='account.move',
        help="",
        copy=True
    )

    check_unsolved = fields.Boolean(
        string='Check Unsolved',
        default=False,
        help="Checks if there's at least an unsolved move in bank paper slip",
        compute="_check_unsolved",
        copy=True
    )

    check_generated_credited_move = fields.Boolean(
        string='Check generated credited move',
        default=False,
        compute="_check_generated_credited_move",
        help="Checks if credited move linked to bank paper slip is generated",
        copy=True
    )

    def _check_generated_credited_move(self):
        self.ensure_one()
        if self.credit_move_id.state == 'draft':
            self.check_generated_credited_move = True
        else:
            self.check_generated_credited_move = False

    def _check_unsolved(self):
        self.ensure_one()
        unsolved_move_ids = self.bank_paper_ids.filtered(lambda l: l.unsolved_move_id.id)
        if len(unsolved_move_ids) > 0:
            self.check_unsolved = True
        else:
            self.check_unsolved = False

    @api.depends('bank_paper_ids')
    def _get_bank_paper_info(self):
        for record in self:
            if record.bank_paper_ids:
                record.company_id = record.bank_paper_ids[0].company_id
                record.currency_id = record.bank_paper_ids[0].currency_id
                record.company_currency_id = record.bank_paper_ids[0].company_currency_id

    def create_bank_paper_slip(self, move_lines, bank_paper_slip_type_id):
        """
        Create bank paper slip. Check if all move lines have an associated partner bank, if not raise an error.
        Group move lines for partner, partner bank and date maturity: create an object with different features based on field group_bank_papers_by_expiration.
        :param ids:
        :return:
        """
        dict_move_line = {}
        # check if companies and currencies are the same in account moves
        if len(move_lines.mapped('company_id')) > 1:
            raise ValidationError(
                _("Unable to create Bank Paper Slip because of account moves have different companies"))
        if len(move_lines.mapped('currency_id')) > 1:
            raise ValidationError(
                _("Unable to create Bank Paper Slip because of account moves have different currencies"))
        # check if invoice of move lines are not in draft
        # INSERIRE MODIFICA CONTROLLO FATTURE NON IN BOZZA NEL MOMENTO DELLA GENERAZIONE DELLA DISTINTA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for line in move_lines:
            if not line.res_partner_bank_id:
                raise ValidationError(_("Some Account Move Line selected doesn't have associated Res Partner Bank"))
            key = (line.partner_id, line.res_partner_bank_id, line.date_maturity)
            move_list = dict_move_line.setdefault(key, self.env['account.move.line'].browse())
            move_list += line
            dict_move_line[key] = move_list
        bank_paper_ids = self.env['l10n_it.bank_paper'].browse([])
        seq_bank_paper = 0
        for key, move_line in dict_move_line.items():
            partner, iban, date_maturity = key
            document_reference = list(set())
            amount = 0
            if partner.group_bank_papers_by_expiration:
                seq_bank_paper += 1
                for move in move_line:
                    amount += move.amount_residual
                    if move.move_id.ref:
                        document_reference.append(move.move_id.ref)
                    else:
                        document_reference.append(move.move_id.name)
                if amount <= 0:
                    raise ValidationError(_("Bank Paper Slip can not have bank papers less than zero"))
                document_reference = ', '.join(document_reference) if len(document_reference) > 0 else ''
                document_date = map(lambda d: format_date(self.env, d), move_line.mapped('date'))
                document_date = list(set(document_date))
                document_date = ', '.join(document_date)
                expiration_date = date_maturity
                account_move_line_ids = move_line.mapped('id')
                list_iban_move_line = move_line.mapped('move_id.invoice_partner_bank_id.id')
                if not all(elem == list_iban_move_line[0] for elem in list_iban_move_line):
                    raise ValidationError(_("Invoice Partner Bank are not the same for every move line"))
                bank_paper_id = self.env['l10n_it.bank_paper'].create({
                    'seq_bank_paper': seq_bank_paper,
                    'type': 'cash_order',
                    'document_reference': document_reference,
                    'document_date': document_date,
                    'amount': amount,
                    'expiration_date': expiration_date,
                    'state': 'draft',
                    'partner_id': partner.id,
                    'partner_bank_id': move_line[0].res_partner_bank_id.id,
                    'account_move_line_ids': [(6, 0, account_move_line_ids)]
                })
                bank_paper_ids += bank_paper_id
            else:
                for move in move_line:
                    seq_bank_paper += 1
                    if move.move_id.type == 'out_refund':
                        raise ValidationError(_("There are move lines relating to credit notes"))
                    document_reference = move.move_id.ref if move.move_id.ref else move.move_id.name
                    document_date = format_date(self.env, move.move_id.date)
                    expiration_date = date_maturity
                    account_move_line_ids = [move.id]
                    amount = move.debit
                    bank_paper_id = self.env['l10n_it.bank_paper'].create({
                        'seq_bank_paper': seq_bank_paper,
                        'type': 'cash_order',
                        'document_reference': document_reference,
                        'document_date': document_date,
                        'amount': amount,
                        'expiration_date': expiration_date,
                        'state': 'draft',
                        'partner_id': partner.id,
                        'partner_bank_id': move.res_partner_bank_id.id,
                        'account_move_line_ids': [(6, 0, account_move_line_ids)]
                    })
                    bank_paper_ids += bank_paper_id
        bank_paper_slip = self.create({
            'bank_paper_slip_type_id': bank_paper_slip_type_id.id,
            'bank_paper_ids': [(6, 0, bank_paper_ids.ids)],
            'total_amount': sum(bank_paper_ids.mapped('amount')),
            'state': 'draft',
            'acceptance_account_move_ids': [(6, 0, move_lines.ids)],
            'release_date': fields.Date.context_today(self)
        })
        return bank_paper_slip

    @api.model
    def create(self, values):
        if 'name' in values:
            return super(L10nItbankPaperSlip, self).create(values)
        seq_riba = self.env.ref('l10n_it_bank_papers.seq_riba', None)
        if not seq_riba:
            raise ValidationError(_("Sequence doesn't exist. Check if it has been deleted."))
        values['name'] = seq_riba.next_by_id(self.acceptance_date)
        return super(L10nItbankPaperSlip, self).create(values)

    def send(self):
        """
        Get stream file with data inside, create object wizard to download riba txt file
        :return:
        """
        self.ensure_one()
        stream = self.create_file_bank_paper_slip()
        self.state = 'sent'
        wizard_id = self.env['file.export.wizard'].create({
            'filename': slugify(self.name),
            'riba_txt': base64.encodebytes(stream.encode())
        })
        x = self.env['ir.attachment'].create({
            'name': "%s" % wizard_id.filename,
            'res_id': self.id,
            'res_model': self._name,
            'datas': wizard_id.riba_txt,
            'type': 'binary'
        })
        view_id = self.env.ref('l10n_it_bank_papers.view_file_export_form').id
        return {
            'name': _("Ri.Ba. Export"),
            'type': 'ir.actions.act_window',
            'res_model': 'file.export.wizard',
            'res_id': wizard_id.id,
            'views': [(view_id, 'form'), (False, 'tree')],
            'target': 'new'
        }

    def accept(self):
        """
        When bank paper slip is in sent state, it must been accepted with specific button. The function creates move object
        for every bank paper and an account move line for every account move line of each bank paper. Then the function reconciles
        account move lines, and the state becomes accepted.
        :return:
        """
        self.ensure_one()
        if not self.acceptance_date:
            self.acceptance_date = fields.Date.context_today(self)
        riba_len = 0
        for riba in self.bank_paper_ids:
            riba_len += 1
            ref = "Ri. Ba. %s -line %s" % (self.name, riba_len)
            move_id = self.env['account.move'].create({
                'ref': ref,
                'invoice_origin': ref,
                'journal_id': self.bank_paper_slip_type_id.acceptance_journal_id.id,
                'date': self.acceptance_date,
                'state': 'draft'
            })
            total_credit = 0
            account_move_list = []
            for account_move_line in riba.account_move_line_ids:
                total_credit += account_move_line.amount_residual
                balance = -account_move_line.amount_residual
                move_line_id = self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'name': ref,
                    'account_id': account_move_line.account_id.id,
                    'partner_id': account_move_line.partner_id.id,
                    'move_id': move_id.id,
                    'is_bank_paper_line': True,
                    'debit': balance if balance > 0 else 0.0,
                    'credit': -balance if balance < 0 else 0.0,
                    'currency_id': account_move_line.currency_id.id if account_move_line and account_move_line.currency_id else None
                })
                account_move_list.append((account_move_line, move_line_id))

            move_line_riba_id = self.env['account.move.line'].create({
                'name': ref,
                'account_id': self.bank_paper_slip_type_id.bank_papers_acceptance_account_account_id.id,
                'partner_id': riba.partner_id.id if riba.partner_id.property_account_receivable_id == self.bank_paper_slip_type_id.bank_papers_acceptance_account_account_id else '',
                'date_maturity': riba.expiration_date,
                'debit': total_credit if total_credit > 0 else 0.0,
                'credit': -total_credit if total_credit < 0 else 0.0,
                'move_id': move_id.id,
                'is_bank_paper_line': True
            })
            move_id.action_post()
            for line in account_move_list:
                mov1, mov2 = line
                (mov1 + mov2).reconcile()
            riba.acceptance_move_id = move_id
            riba.state = 'accepted'
        self.state = 'accepted'

    def accredit(self):
        """
        Open wizard to show summary of account move is going to create for accreditation.
        :return:
        """
        self.ensure_one()
        amount = sum(self.bank_paper_ids.mapped('amount'))
        if amount == 0:
            raise ValidationError(_("It's not possible to continue because amount is 0"))
        bank_paper_slip_summary_wizard_id = self.env['l10n_it.bank_paper.slip.summary.wizard'].create({
            'journal_id': self.bank_paper_slip_type_id.credit_journal_id.id if self.bank_paper_slip_type_id.credit_journal_id.id else None,
            'account_id': self.bank_paper_slip_type_id.bank_papers_credit_account_account_id.id if self.bank_paper_slip_type_id.bank_papers_credit_account_account_id.id else None,
            'bank_account_id': self.bank_paper_slip_type_id.bank_credit_account_account_id.id if self.bank_paper_slip_type_id.bank_credit_account_account_id else None,
            'bank_expense_account_id': self.bank_paper_slip_type_id.bank_charges_credit_account_account_id.id if self.bank_paper_slip_type_id.bank_charges_credit_account_account_id else None,
            'amount': amount,
            'bank_amount': amount,
            'expense_amount': 0
        })
        view_id = self.env.ref('l10n_it_bank_papers.view_bank_paper_slip_accreditation_summary_form').id
        return {
            'name': _("Bank Paper Slip Accreditation Summary"),
            'type': 'ir.actions.act_window',
            'res_model': 'l10n_it.bank_paper.slip.summary.wizard',
            'views': [(view_id, 'form'), (False, 'tree')],
            'res_id': bank_paper_slip_summary_wizard_id.id,
            'target': 'new'
        }


    def recordIb(self):
        sia_code = self.company_id.sia_code if self.company_id.sia_code else ''
        sia_code = sia_code.rjust(5, '0')
        abi_code = self.bank_paper_slip_type_id.company_bank_account_id.sanitized_acc_number[5:10] if self.bank_paper_slip_type_id.company_bank_account_id.acc_number else ''
        abi_code = abi_code.rjust(5, '0')
        release_date = self.release_date.strftime('%d%m%y') if self.release_date else ''
        release_date = release_date.rjust(6, '0')
        support_name = datetime.datetime.now().strftime("%d%m%y%H%M%S") + sia_code
        support_name = support_name.ljust(20, ' ')
        divisa_code = 'E'
        return " IB" + sia_code + abi_code + release_date + support_name + " " * 74 + divisa_code + " " * 6 + "\r\n"

    def record14(self, riba, progressivo):
        progressivo = str(progressivo).rjust(7, '0')
        due_date = riba.document_date[0:2] + riba.document_date[3:5] + riba.document_date[8:10]
        amount = str(int(round(riba.amount * 100)))
        amount = amount.rjust(13, '0')
        abi_code = self.bank_paper_slip_type_id.company_bank_account_id.sanitized_acc_number[
                   5:10] if self.bank_paper_slip_type_id.company_bank_account_id.sanitized_acc_number else ''
        abi_code = abi_code.rjust(5, '0')
        cab_code = self.bank_paper_slip_type_id.company_bank_account_id.sanitized_acc_number[
                   10:15] if self.bank_paper_slip_type_id.company_bank_account_id.sanitized_acc_number else ''
        cab_code = cab_code.rjust(5, '0')
        account_code = riba.partner_bank_id.sanitized_acc_number[-12:] if riba.partner_bank_id.sanitized_acc_number else ''
        account_code = account_code.ljust(12, '0')
        abi_code_line = riba.partner_bank_id.sanitized_acc_number[5:10] if riba.partner_bank_id.sanitized_acc_number else ''
        abi_code_line = abi_code_line.rjust(5, '0')
        cab_code_line = riba.partner_bank_id.sanitized_acc_number[10:15] if riba.partner_bank_id.sanitized_acc_number else ''
        cab_code_line = cab_code_line.rjust(5, '0')
        sia_code = riba.company_id.sia_code if riba.company_id.sia_code else ''
        sia_code = sia_code.rjust(5, '0')
        partner_code_line = riba.partner_id.ref if riba.partner_id.ref else ''
        partner_code_line = partner_code_line.ljust(16, ' ')
        divisa_code = 'E'
        return " 14" + progressivo + " " * 12 + due_date + "30000" + amount + "-" \
               + abi_code + cab_code + account_code + abi_code_line + cab_code_line \
               + " " * 12 + sia_code + "4" + partner_code_line + " " * 6 + divisa_code + "\r\n"

    def record20(self, riba, progressivo):
        progressivo = str(progressivo).rjust(7, '0')
        company_name = riba.company_id.name[:24] if riba.company_id.name else ''
        company_name = company_name.ljust(24, ' ')
        company_street = riba.company_id.partner_id.street[:24] if riba.company_id.partner_id.street else ''
        company_street = company_street.ljust(24, ' ')
        company_cap = riba.company_id.partner_id.zip if riba.company_id.partner_id.zip else ''
        company_cap = company_cap.ljust(24, ' ')
        company_ref = riba.company_id.partner_id.ref if riba.company_id.partner_id.ref else ''
        company_ref = company_ref.ljust(24, ' ')
        return " 20" + progressivo + company_name + company_street + company_cap + company_ref + " " * 14 + "\r\n"

    def record30(self, riba, progressivo):
        progressivo = str(progressivo).rjust(7, '0')
        partner_name = riba.partner_id.name if riba.partner_id.name else ''
        partner_name = partner_name.ljust(60, ' ')
        partner_name = partner_name[:60]
        partner_cf = riba.partner_id.vat if riba.partner_id.vat else ''
        partner_cf = partner_cf.ljust(16, ' ')
        partner_cf = partner_cf[2:]
        return " 30" + progressivo + partner_name + partner_cf + " " * 34 + "\r\n"

    def record40(self, riba, progressivo):
        progressivo = str(progressivo).rjust(7, '0')
        partner_address = riba.partner_id.street if riba.partner_id.street else ''
        partner_address = partner_address.ljust(30, ' ')
        partner_address = partner_address[:30]
        partner_cap = riba.partner_id.zip if riba.partner_id.zip else ''
        partner_cap = partner_cap.rjust(5, '0')
        partner_city = riba.partner_id.city if riba.partner_id.city else ''
        partner_state_code = riba.partner_id.state_id.code if riba.partner_id.state_id.code else ''
        partner_state_code = partner_state_code.rjust(25 - len(partner_city), ' ')
        com_prov = partner_city + partner_state_code
        partner_bank = riba.partner_bank_id.bank_id.name if riba.partner_bank_id.bank_id.name else ''
        partner_bank = partner_bank.ljust(50, ' ')
        partner_bank = partner_bank[:50]
        return " 40" + progressivo + partner_address + partner_cap + com_prov + partner_bank + "\r\n"

    def record50(self, riba, progressivo):
        progressivo = str(progressivo).rjust(7, '0')
        document_date = riba.document_date[6:10] + '-' + riba.document_date[3:5] + '-' + riba.document_date[0:2]
        description = "PER LA FATTURA N. " + riba.document_reference + " DEL " + document_date + " IMP " + str(
            riba.amount)
        description = description.ljust(80, ' ')
        description = description[:80]
        company_vat = riba.company_id.vat if riba.company_id.vat else ''
        company_vat = company_vat.ljust(16, ' ')
        company_vat = company_vat[2:]
        return " 50" + progressivo + description + " " * 10 + company_vat + " " * 4 + "\r\n"

    def record51(self, riba, progressivo):
        progressivo = str(progressivo).rjust(7, '0')
        id = str(riba.id)
        id = id.rjust(10, '0')
        company_name = riba.company_id.name[:20]
        return " 51" + progressivo + id + company_name + " " * 80 + "\r\n"

    def record70(self, riba, progressivo):
        progressivo = str(progressivo).rjust(7, '0')
        return " 70" + progressivo + " " * 110 + "\r\n"

    def recordEf(self, progressivo, total_amount,number_of_line):
        sia_code = self.company_id.sia_code if self.company_id.sia_code else ''
        sia_code = sia_code.rjust(5, '0')
        abi_code = self.bank_paper_slip_type_id.company_bank_account_id.sanitized_acc_number[5:10]
        abi_code = abi_code.rjust(5, '0')
        release_date = self.release_date.strftime('%d%m%y')
        release_date = release_date.rjust(6, '0')
        support_name = datetime.datetime.now().strftime("%d%m%y%H%M%S") + sia_code
        support_name = support_name.ljust(20, ' ')
        codice_divisa = 'E'
        total_progr = number_of_line
        total_progr = str(total_progr).rjust(7, '0')
        progressivo = str(progressivo).rjust(7, '0')
        return " EF" + sia_code + abi_code + release_date + support_name + " " * 6 + progressivo + total_amount \
               + "0" * 15 + str(total_progr) + " " * 24 + codice_divisa + " " * 6 + "\r\n"

    def create_file_bank_paper_slip(self):
        """
        Create stream file to write inside head and lines of riba file txt
        :return:
        """
        stream = StringIO()
        progressivo = 0
        stream.write(self.recordIb())
        total_amount = 0
        number_of_line = 0
        for riba in self.bank_paper_ids:
            progressivo += 1
            number_of_line += progressivo
            stream.write(self.record14(riba, progressivo))
            number_of_line += 1
            stream.write(self.record20(riba, progressivo))
            number_of_line += 1
            stream.write(self.record30(riba, progressivo))
            number_of_line += 1
            stream.write(self.record40(riba, progressivo))
            number_of_line+=1
            stream.write(self.record50(riba, progressivo))
            number_of_line += 1
            stream.write(self.record51(riba, progressivo))
            number_of_line += 1
            stream.write(self.record70(riba, progressivo))
            total_amount += riba.amount
        total_amount = str(int(round(total_amount * 100, 2))).rjust(15, '0')
        number_of_line += 1
        stream.write(self.recordEf(progressivo, total_amount, number_of_line))
        stream.seek(0)
        return stream.read()

    def view_unsolved_move(self):
        for record in self:
            unsolved_move_ids = record.bank_paper_ids.mapped('unsolved_move_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bank Paper Slip Accreditation',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.move',
            'domain': [('id', 'in', unsolved_move_ids)]
        }

    def unlink(self):
        for record in self:
            # check if bank paper slip is in draft state, if it's not, it's not possible to delete it
            if record.filtered(lambda d: d.state != 'draft'):
                raise ValidationError(_("It's possible delete a Bank Paper Slip only in the Draft state"))
            # check if every bank paper is in draft state, if just one is not draft, it's not possible to delete bank paper slip
            bank_paper_ids = record.mapped('bank_paper_ids').filtered(
                lambda l: l.state != 'draft'
            )
            '''if len(bank_paper_ids) > 0:
                raise ValidationError(_("It's possible delete a Bank Paper Slip only if all Bank Papers are in the Draft state"))'''
            # check reconcile after to delete bank paper slip
            move_line_riba = record.env['account.partial.reconcile']
            move_line_riba += record.mapped('bank_paper_ids.account_move_line_ids.matched_credit_ids')
            move_line_riba += record.mapped('bank_paper_ids.account_move_line_ids.matched_debit_ids')
            if any([x for x in move_line_riba]):
                raise ValidationError(_("It's not possible to delete Bank Paper. First you have to cancel reconcile"))
        return super(L10nItbankPaperSlip, self).unlink()

    def view_credited_move(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bank Paper Slip Accreditation',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.move',
            'domain': [('id', '=', self.credit_move_id.id)]
        }

    def view_accepted_move(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Acceptance Move',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.mapped('bank_paper_ids.acceptance_move_id.id'))]
        }
