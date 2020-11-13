# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _prepare_payment_moves(self):
        '''
        Inherit prepare_payment_moves and change value of date_maturity
        :return: all moves create without date_maturity
        '''
        all_moves = super(AccountPayment, self)._prepare_payment_moves()
        for move_dict in all_moves:
            if not move_dict.get('line_ids',False):
                continue
            line_ids = move_dict.get('line_ids',False)
            if not line_ids:
                continue
            for line in line_ids:
                line_dict = line[2]
                if not line_dict:
                    continue
                line_dict['date_maturity'] = False
        return all_moves