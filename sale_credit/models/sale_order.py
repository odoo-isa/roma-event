# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        # Check that credit limit is sufficient only if sale credit type is value
        if self.partner_id.sale_credit_type == 'value':
            if self.partner_id.remaing_credit < 0.0 or self.partner_id.remaing_credit < self.amount_total:
                raise ValidationError(_("It is not possible to confirm the order because the limit credit exceeded"))
        res = super(SaleOrder, self).action_confirm()
        return res

