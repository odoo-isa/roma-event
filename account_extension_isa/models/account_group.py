# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountGroup(models.Model):
    _inherit = 'account.group'

    account_ids = fields.One2many(
        string='Account ',
        comodel_name='account.account',
        inverse_name='group_id',
        help="""The accounts that has this group""",
        copy=False,
    )

    absolute_path_name = fields.Char(
        string='Complete parent name',
        help='''The complete name of the parent record''',
        copy=False,
        compute="_compute_absolute_path_name",
        store=True,
    )

    @api.depends('name', 'code_prefix', 'parent_id.absolute_path_name')
    def _compute_absolute_path_name(self):
        for group in self:
            if not group.parent_path:
                continue
            absolute_path = group.parent_path.split('/')
            absolute_path = absolute_path[:-2]
            if not absolute_path:
                group.absolute_path_name = '/'
                continue
            path_name = [
                "%s %s" % (self.browse(int(group_id)).code_prefix, self.browse(int(group_id)).name)
                for group_id in absolute_path
            ]
            path_name = '/'.join(path_name)
            group.absolute_path_name = path_name
