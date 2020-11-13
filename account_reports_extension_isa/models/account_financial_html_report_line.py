# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountFinancialHtmlReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    report_name = fields.Char(
        string='Report name',
        related="report_root_id.name",
        readonly=True,
        help="Name of the financial report of this section",
        copy=False,
        store=True,
    )

    complete_name = fields.Char(
        string='Complete name',
        help='''Complete name of the section's path''',
        copy=False,
        compute="_compute_complete_name"
    )

    filter_mode = fields.Selection(
        string='Filter mode',
        required=True,
        default='domain',
        selection=[('domain', 'By domain'), ('account', 'By account list')],
        help='''Which mode have to be used for the select of the accounts:
* By domain - The user that configure report must be specify domain (according to the Odoo domain syntax)
* By account list - The user must be specify accounts individually.''',
        copy=False,
    )

    domain_account_ids = fields.Many2many(
        string='Accounts for this section',
        comodel_name='account.account',
        relation='account_report_line_account_rel',
        column1='account_report_line_id',
        column2='account_id',
        help='''If filter mode is set with 'By account list' should be enumerate the accounts to considering for this
         report section''',
        copy=False,
    )

    report_root_id = fields.Many2one(
        string='Report html root',
        comodel_name='account.financial.html.report',
        compute="_get_report_root",
        store=True,
        help="The report root id in nested report line",
        readonly=True
    )

    absolute_path_name = fields.Char(
        string='Complete parent name',
        help='''The complete name of the parent record''',
        copy=False,
        compute="_compute_absolute_path_name",
        store=True,
    )

    @api.depends('parent_path')
    def _get_report_root(self):
        for record in self:
            line_root = record.parent_path.split('/')
            if not line_root:
                continue
            line_root = int(line_root[0])
            line_report_root = self.browse(line_root)
            record.report_root_id = line_report_root.financial_report_id

    @api.depends('name', 'parent_id.absolute_path_name')
    def _compute_absolute_path_name(self):
        for report_line in self:
            if not report_line.parent_path:
                continue
            absolute_path = report_line.parent_path.split('/')
            absolute_path = absolute_path[:-2]
            if not absolute_path:
                report_line.absolute_path_name = '/'
                continue
            path_name = [self.browse(int(report_line_id)).name for report_line_id in absolute_path]
            path_name = '/'.join(path_name)
            report_line.absolute_path_name = path_name

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for report_line in self:
            if report_line.parent_id:
                report_line.complete_name = '%s/%s' % (report_line.parent_id.complete_name, report_line.name)
            else:
                report_line.complete_name = report_line.name

    @api.onchange('filter_mode')
    def _onchange_filter_mode(self):
        """
        Clear the filter's fields according to the filter mode.
        :return: void
        """
        if self.filter_mode == 'domain':
            self.domain = None
            self.domain_account_ids = None

    def create(self, vals):
        """
        If filter mode is account set fixed domain to work with this logic.
        :param vals: write value
        :return: Object of account html report line
        """
        res = super(AccountFinancialHtmlReportLine, self).create(vals)
        if 'filter_mode' in vals and vals['filter_mode'] == 'account':
            res.domain = "[('account_id.html_report_line_section_ids', 'in', %d)]" % res.id
        return res

    def write(self, vals):
        """
        If filter mode is account set fixed domain to work with this logic.
        :param vals: write value
        :return: Bool
        """
        if 'filter_mode' in vals and vals['filter_mode'] == 'account':
            domain = "[('account_id.html_report_line_section_ids', 'in', %d)]" % self.id
            vals.update(domain=domain)
        return super(AccountFinancialHtmlReportLine, self).write(vals)

    @api.constrains('domain_account_ids')
    def _check_same_account_on_report(self):
        accounts = self.mapped('domain_account_ids')
        accounts.check_same_account_on_report()
