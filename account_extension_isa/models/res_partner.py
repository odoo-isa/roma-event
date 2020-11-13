# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('bank_ids')
    def check_default_bank(self):
        """
        The method introduces the control on the default bank setting on the customer / supplier: a maximum of one
        default bank can be associated
        :return:
        """
        if self.bank_ids and self.bank_ids.filtered(lambda b: not b.default) and not self.bank_ids.filtered(
                lambda b: b.default):
            raise ValidationError(_('''The Customer/Supplier must have an associated default bank. 
                                      Correct the error to proceed.'''))
        if self.bank_ids and len(self.bank_ids.filtered(lambda b: b.default)) > 1:
            raise ValidationError(_('''The Customer/Supplier must have an associated at most one default bank. 
                                                  Correct the error to proceed.'''))