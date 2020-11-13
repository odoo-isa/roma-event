# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api,_
from datetime import date


class ResPartner(models.Model):
    _inherit = 'res.partner'

    birthday = fields.Date(
        string='Birthday',
        help='If set, we will send a greeting email on the birthday',
    )

    @api.model
    def _cron_happy_birthday_mail(self):
        self.env.cr.execute( """
                 SELECT *
                 FROM res_partner
                 WHERE EXTRACT(DAY FROM birthday) = EXTRACT(DAY from CURRENT_TIMESTAMP) and
                 EXTRACT(month FROM birthday) = EXTRACT(month from CURRENT_TIMESTAMP)
            """)
        partners_birthday = self.env.cr.dictfetchall()
        for partner in partners_birthday:
            template_id = self.env['ir.model.data'].get_object_reference(
                'base_partner_happy_birthday', 'base_partner_happy_birthday_template')
            if template_id:
                self.env['mail.template'].browse(template_id[1]).send_mail(partner['id'], force_send=True)
        return

