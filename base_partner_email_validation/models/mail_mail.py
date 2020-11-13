# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        recipient_ids = self.recipient_ids.filtered(lambda r: r.is_verified_email or not r.verification_email_sent)
        if len(recipient_ids) > 0:
            self.write({
                'recipient_ids': recipient_ids
            })
        return super(MailMail, self).send(auto_commit=auto_commit, raise_exception=raise_exception)
