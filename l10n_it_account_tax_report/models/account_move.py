# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    original_move_id = fields.Many2one(
        string="Registrazione Contabile d'Origine",
        required=False,
        readonly=True,
        comodel_name='account.move',
        ondelete='cascade',
        help="Viene impostato ogni volta che viene effettuata una Registrazione con movimenti contabili in credito e "
             "di conto erario",
        copy=False
    )
    delegated_move_id = fields.Many2one(
        string='Registrazione Competenza a Periodo Successivo',
        required=False,
        readonly=True,
        comodel_name='account.move',
        ondelete='cascade',
        help="Registrazione Contabile creata quando ci sono movimenti contabili di tipo conto erario",
        copy=False,
    )

    def get_conti_erario(self):
        """
        Ritorna una lista di conti erario tra tutti i gruppi imposta
        :return: List
        """
        conti_erario_obj = self.env['account.account']
        list_conti_erario = []
        # Cerco, tra tutti i Gruppi d'imposta, i relativi conti erario associati
        all_account_tax_groups = self.env['account.tax.group'].search([])
        for account_tax_group_obj in all_account_tax_groups:
            tax_payable_account_id = account_tax_group_obj.property_tax_payable_account_id
            tax_receivable_account_id = account_tax_group_obj.property_tax_receivable_account_id
            advance_tax_payment_account_id = account_tax_group_obj.property_advance_tax_payment_account_id
            conti_erario_obj += tax_payable_account_id | tax_receivable_account_id | advance_tax_payment_account_id
        if conti_erario_obj:
            conti_erario_obj = conti_erario_obj.mapped('id')
            list_conti_erario = list(set(conti_erario_obj))
        return list_conti_erario

    def update_move_lines(self, original_move_lines, new_account_move_obj):
        """
        :param original_move_lines: Object
        :param new_account_move_obj: Object
        """
        # Duplico le move lines filtrate: nel contesto passo il parametro "check_move_validity" a False perché
        # altrimenti viene effettuato un controllo sul bilancio tra credito e debito: in questo caso non c'è
        # bisogno di effettuare questo controllo in quanto viene creata per ogni riga di conto erario:
        # * una riga di debito
        # * una riga di credito
        new_account_move_obj.line_ids.unlink()
        for original_move_line_obj in original_move_lines:
            credit = original_move_line_obj.debit - original_move_line_obj.credit
            # Credito
            self.env['account.move.line'].with_context(check_move_validity=False).create({
                'name': 'Payable tax amount',
                'move_id': new_account_move_obj.id,
                'debit': 0.0,
                'credit': credit,
                'account_id': original_move_line_obj.account_id.id
            })
            # Debito
            debit_move_line_obj = self.env['account.move.line'].with_context(check_move_validity=False).create({
                'name': 'Receivable tax amount',
                'move_id': new_account_move_obj.id,
                'debit': credit,
                'credit': 0.0,
                'account_id': original_move_line_obj.account_id.id
            })
            external_tag_id = 'l10n_it_account_tax_report.tax_report_title_taxes_previous_balance_credit'
            account_tax_report_line_obj = self.env.ref(external_tag_id, False)
            if account_tax_report_line_obj:
                tag_obj = account_tax_report_line_obj.tag_ids.filtered(lambda t: t.tax_negate)
                tag_ids = tag_obj.ids if tag_obj else []
                debit_move_line_obj.write({'tag_ids': [(6, 0, tag_ids)]})

    def duplicate_move(self, conti_erario_ids):
        """
        Viene duplicata una Registrazione contabile se sono presenti movimenti contabili in dare per ogni conto erario
        :param conti_erario_ids: List
        :return Object (Nuova Registrazione Contabile)
        """
        # Per ogni conto erario filtrato, controllo se ci sono i relativi movimenti contabili
        original_move_lines_obj = self.env['account.move.line']
        for conto_erario_id in conti_erario_ids:
            filtered_move_lines = self.line_ids.filtered(
                lambda aml: aml.account_id.id == conto_erario_id and aml.debit > 0
            )
            if not filtered_move_lines:
                continue
            original_move_lines_obj = original_move_lines_obj | filtered_move_lines
        # Se è già presente la Registrazione Figlia, allora provvedo ad aggiornare i movimenti contabili
        delegated_move_obj = self.delegated_move_id
        if delegated_move_obj:
            self.update_move_lines(original_move_lines_obj, delegated_move_obj)
            return delegated_move_obj
        # Se non è presente la Registrazione Figlia ed esistono movimenti di tipo conto erario, la creo (account.move)
        new_account_move_obj = None
        if original_move_lines_obj:
            # Data di riferimento: primo giorno al mese successivo
            next_month_date = self.date + relativedelta(months=+1)
            account_move_date = next_month_date.replace(day=1)
            new_account_move_obj = self.env['account.move'].create({
                'ref': self.ref + ' (Copia Informativa)',
                'date': account_move_date,
                'journal_id': self.journal_id.id,
                'original_move_id': self.id
            })
            self.update_move_lines(original_move_lines_obj, new_account_move_obj)
            # Associo le Registrazione figlia alla Registrazione Contabile Padre
            self.write({'delegated_move_id': new_account_move_obj.id})
        return new_account_move_obj

    def action_post(self):
        """
        Questa funzione permette di creare una nuova Registrazione Contabile nel caso in siano presenti movimenti
        contabili con conto erario
        """
        res = super(AccountMove, self).action_post()
        conti_erario_ids = self.get_conti_erario()
        if conti_erario_ids:
            new_account_move_obj = self.duplicate_move(conti_erario_ids)
            if new_account_move_obj:
                # Richiamo il metodo che permette la registrazione
                new_account_move_obj.post()
        return res

    def button_draft(self):
        """
        Se la registrazione padre viene impostata in bozza, allora viene messa in questo stato anche la Registrazione
        contabile figlia
        """
        res = super(AccountMove, self).button_draft()
        delegated_move_obj = self.delegated_move_id
        if delegated_move_obj:
            delegated_move_obj.button_draft()
        return res

    def button_cancel(self):
        """
        Se la registrazione padre viene annullata, allora viene messa in questo stato anche la Registrazione
        contabile figlia
        """
        res = super(AccountMove, self).button_cancel()
        delegated_move_obj = self.delegated_move_id
        if delegated_move_obj:
            delegated_move_obj.button_cancel()
        return res

    @api.onchange('line_ids', 'invoice_payment_term_id', 'invoice_date_due', 'invoice_cash_rounding_id', 'invoice_vendor_bill_id')
    def _onchange_recompute_dynamic_lines(self):
        if not self.line_ids and self.delegated_move_id:
            for line_obj in self.delegated_move_id.line_ids:
                line_obj.unlink()
        return super(AccountMove, self)._onchange_recompute_dynamic_lines()

    def write(self, vals):
        # Aggiorno la testata della Registrazione Figlia se è presente
        if self.delegated_move_id:
            self.delegated_move_id.write({'ref': self.ref})
        return super(AccountMove, self).write(vals)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # Non permetto la copia di una Registrazione Informativa
        if self.original_move_id:
            raise ValidationError("Non è possibile duplicare una Registrazione Informativa!")
        return super(AccountMove, self).copy(default)

    def action_switch_invoice_into_refund_credit_note(self):
        # Switch invoice into refund credit note
        if self.original_move_id:
            raise ValidationError("Non è possibile trasformare la Registrazione Informativa in Nota di Credito!")
        return super(AccountMove, self).action_switch_invoice_into_refund_credit_note()
