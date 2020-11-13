# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, _


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_compute_recipients(self, message, msg_vals):
        """
        Inherit this method for delete all followers without valid email
        """
        res = super(MailThread, self)._notify_compute_recipients(message, msg_vals)
        if 'partners' in res.keys():
            for element in res['partners']:
                partner_id = element['id']
                notif = element['notif']
                partner_obj = self.env['res.partner'].browse(partner_id)
                if partner_obj.verification_email_sent and not partner_obj.is_verified_email and notif == 'email':
                    element['notif'] = None
                    message = (_("For user %s  it wasn't possible to send communication because doesn't have a valid "
                                 "email address!") % partner_obj.name
                               )
                    # Notify with not valid mail for partner in message log
                    self.message_post(body=message)
        return res
