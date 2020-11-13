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


class WizardReportAccountingEntry(models.TransientModel):
    _name = "wizard.report.accounting.entry"
    _description = "Wizard report accounting entry"

    partner_id = fields.Many2one(
        string='Partner',
        required=True,
        comodel_name='res.partner',
        help="",
        copy=False
    )

    state = fields.Selection(
        string='State',
        required=True,
        selection=[('open', 'Open'), ('close', 'Close')],
        help="",
        copy=False
    )

    include_draft = fields.Boolean(
        string='Include draft',
        default=False,
        help="",
        copy=False
    )

    def print_report(self):
        self.ensure_one()
        l10n_it_accounting_entry_ids = self.env['l10n_it.accounting.entry'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', self.state)
        ])
        if not l10n_it_accounting_entry_ids:
            raise ValidationError(_("There are not reports to print"))
        data = {
            'include_draft': self.include_draft
        }
        return self.env.ref('l10n_it_accounting_entry.action_report_accounting_entry').report_action(l10n_it_accounting_entry_ids.ids, data=data)
