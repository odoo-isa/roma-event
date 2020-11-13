# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class SelectBankPaperSlipTypeWizard(models.TransientModel):
    _name = 'select.bank_paper.slip.type.wizard'
    _description = 'Choose Bank Paper Slip Type'

    bank_paper_slip_type_id = fields.Many2one(
        string='Bank Paper Slip Type',
        required=True,
        readonly=False,
        comodel_name='l10n_it.bank_paper.slip.types',
        help='It allows to choose bank paper slip type to create bank paper slip object',
        copy=False,
    )

    def create_bank_paper_slip(self):
        """
        check if model is right and link to bank paper slip form with view id
        :return: a form view to show bank paper slip creation
        """
        self.ensure_one()
        if self._context['active_model'] != 'account.move.line':
            raise ValidationError(_("Active model is not 'account.move.line'"))
        move_line_ids = self.env['account.move.line'].browse(self._context['active_ids'])
        bank_paper_slip = self.env['l10n_it.bank_paper.slip'].create_bank_paper_slip(move_line_ids, self.bank_paper_slip_type_id)
        view_id = self.env.ref('l10n_it_bank_papers.view_bank_paper_slip_form').id
        return {
            'name': _("Bank Paper Slip"),
            'type': "ir.actions.act_window",
            'res_model': 'l10n_it.bank_paper.slip',
            'views': [(view_id, 'form')],
            'res_id': bank_paper_slip.id,
            'target': 'current'
        }
