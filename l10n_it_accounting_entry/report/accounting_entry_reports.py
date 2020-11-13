# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountingEntryReports(models.AbstractModel):
    _name = "report.l10n_it_accounting_entry.report_accounting_entry"
    _description = "Accounting Entry Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('l10n_it_accounting_entry.report_accounting_entry')
        entry_ids = self.env['l10n_it.accounting.entry'].browse(data['context']['active_ids'])
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': entry_ids,
            'include_draft': data['include_draft']
        }
        return docargs
