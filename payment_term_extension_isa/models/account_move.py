# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _create_account_move_lines(self, balance, amount_currency, date_maturity, account, **kwargs):
        """
        Inherits (from "account_patch_isa") method to create a dictionary with values for create a account.move.line
        :param balance: if price > 0 then debit = price; if price < 0 then credit = - price
        :param amount_currency: amount_currency of the account_move_line
        :param currency_id: currency linked to the account_move_line
        :param date_maturity: date maturity of the account_move_line
        :return:
        """
        res = super(AccountMove, self)._create_account_move_lines(balance, amount_currency, date_maturity, account, **kwargs)
        # Add Payment Type
        if 'payment_type_id' in kwargs:
            res.update({
                'payment_type_id': kwargs.get('payment_type_id', False)
            })
        return res

    def _get_candidate(self, candidate, date_maturity, balance, amount_currency, **kwargs):
        """
        Inherits (from "account_patch_isa") method to update dictionary with payment type values for create a account.move.line
        :param balance: if price > 0 then debit = price; if price < 0 then credit = - price
        :param amount_currency: amount_currency of the account_move_line
        :param currency_id: currency linked to the account_move_line
        :param date_maturity: date maturity of the account_move_line
        :return:
        """
        res = super(AccountMove, self)._get_candidate(candidate, date_maturity, balance, amount_currency, **kwargs)
        res.update({
            'payment_type_id': False
        })
        # Add Payment Type
        if 'payment_type_id' in kwargs:
            res.update({
                'payment_type_id': kwargs.get('payment_type_id', False)
            })
        return res
