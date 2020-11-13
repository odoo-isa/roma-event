# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, api, _
from logging import getLogger
from odoo.exceptions import ValidationError

_logger = getLogger(__name__)


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    @api.onchange('analytic_distribution_ids', 'analytic_distribution_ids.percentage')
    def _onchange_analytic_distribution_ids(self):
        sum_percentage = sum(distribution.percentage for distribution in self.analytic_distribution_ids)
        if not 0 <= sum_percentage <= 100:
            raise ValidationError(_("Total percentage for all rows should be between 0 and 100"))
