# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from dateutil.relativedelta import relativedelta
from logging import getLogger

_logger = getLogger(__name__)


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    def compute(self, value, date_ref=False, currency=None):
        """
        This function is override (original's method is in "account->account_invoice.py)
        :param value: Integer
        :param date_ref: Date
        :return: Dict
        """
        date_ref = date_ref or fields.Date.today()
        amount = value
        sign = value < 0 and -1 or 1
        result = []
        if not currency:
            currency = self.env.user.company_id.currency_id
        for line in self.line_ids:
            amt = 0
            if line.value == 'fixed':
                amt = sign * currency.round(line.value_amount)
            elif line.value == 'percent':
                amt = currency.round(value * (line.value_amount / 100.0))
            elif line.value == 'balance':
                amt = currency.round(amount)
            if amt:
                next_date = fields.Date.from_string(date_ref)
                if line.option == 'day_after_invoice_date':
                    next_date += relativedelta(days=line.days)
                    if line.day_of_the_month > 0:
                        months_delta = (line.day_of_the_month < next_date.day) and 1 or 0
                        next_date += relativedelta(day=line.day_of_the_month, months=months_delta)
                elif line.option == 'after_invoice_month':
                    next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                    next_date = next_first_date + relativedelta(days=line.days - 1)
                elif line.option == 'day_following_month':
                    next_date += relativedelta(day=line.days, months=1)
                elif line.option == 'day_current_month':
                    next_date += relativedelta(day=line.days, months=0)
                result.append((fields.Date.to_string(next_date), amt, line._get_custom_data()))
                amount -= amt
        amount = sum(amt for _, amt, _, in result)
        dist = currency.round(value - amount)
        if dist:
            last_date = result and result[-1][0] or fields.Date.today()
            result.append((last_date, dist, None))
        return result
