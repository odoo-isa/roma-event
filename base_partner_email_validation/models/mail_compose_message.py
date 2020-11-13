# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def send_mail(self, auto_commit=False):
        # Check that email's recipients users as verified email
        partner_ids = self.partner_ids.filtered(lambda p: p.is_verified_email or not p.verification_email_sent)
        if len(partner_ids) > 0:
            self.write({
                'partner_ids': partner_ids
            })
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
