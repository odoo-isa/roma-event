# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = 'account.account'

    html_report_line_section_ids = fields.Many2many(
        string='Financial Reports',
        index=True,
        comodel_name='account.financial.html.report.line',
        relation='account_report_line_account_rel',
        column1='account_id',
        column2='account_report_line_id',
        help="This account will be included in this report sections.",
        copy=False
    )

    @api.constrains('html_report_line_section_ids')
    def check_same_account_on_report(self):
        """
        An account must to be present only in one report section. Multiple report's sections with same account is not
        admitted.
        :return: void
        :raise: ValidationError
        """
        for account in self:
            in_sections = self.env['account.financial.html.report.line'].read_group(
                domain=[('id', 'in', account.html_report_line_section_ids.ids)],
                fields=['report_root_id'],
                groupby=['report_root_id']
            )
            in_sections = list(filter(lambda d: d['report_root_id_count'] > 1, in_sections))
            if in_sections:
                in_sections = in_sections[0]
                report_name = in_sections['report_root_id'][1]
                sections = self.env['account.financial.html.report.line'].search(in_sections['__domain'])
                sections_name = list(set(sections.mapped('name')))
                raise ValidationError(
                    _("The account '%s' is present in more than one section for the report '%s': \n%s") %
                    (account.name, report_name, ', '.join(sections_name))
                )
