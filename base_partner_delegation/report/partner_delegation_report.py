# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class PartnerDelegationReport(models.AbstractModel):
    _name = "report.base_partner_delegation.print_delegations"
    _description = "Report to print partner delegations"

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('base_partner_delegation.print_delegations')
        # get the partner of delegation with context and return that partner plus parent partner who delegated
        active_model = data['context'].get('active_model', False)
        active_id = data['context'].get('active_id', False)
        res_partner_delegation = self.env[active_model].browse(active_id)
        # customize report name
        report.name = _("Delegation model %s" % res_partner_delegation.partner_delegate_id.name)
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': res_partner_delegation
        }
        return docargs
