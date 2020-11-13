# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import random
import werkzeug.urls
from odoo.exceptions import UserError, ValidationError


def random_email_token():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(16))


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_verified_email = fields.Boolean(
        string='Is verified email',
        help="Indicates if email has been verified",
        copy=False,
        default=False
    )
    verification_email_token = fields.Char(
        string="Verification email token",
        size=16,
        help="Indicates token used to verify email",
        copy=False
    )
    verification_email_sent = fields.Boolean(
        string='Verification email sent',
        help="Indicates whether email has been sent to address",
        copy=False,
    )
    verification_email_url = fields.Char(
        string='Verification email url',
        help="Indicates url to be used confirm email",
        copy=False,
        store=True
    )

    @api.onchange('email')
    def onchange_email(self):
        self.is_verified_email = False
        self.verification_email_token = None
        self.verification_email_sent = False
        self.verification_email_url = None
        super(ResPartner, self).onchange_email()

    def write(self, vals):
        """ If email is changed, token's field are also cleaned """
        if 'email' in vals:
            vals['is_verified_email'] = False
            vals['verification_email_token'] = None
            vals['verification_email_url'] = None
        return super(ResPartner, self).write(vals)

    def verified_email_sent(self):
        """ This method invoked template with a link to confirm relative email """
        self.ensure_one()
        try:
            if not self.email:
                raise UserError(_("There isn't mail to verify"))
            if self.verification_email_sent:
                raise UserError(_("This mail is already verified"))
            # Generate Token
            token = random_email_token()
            # Generate url for confirm mail
            base_url = self.get_base_url()
            route = 'email/validate'
            query = dict(db=self.env.cr.dbname)
            query['id'] = self.id
            query['token'] = token
            url = base_url + "/web/%s?%s" % (route, werkzeug.urls.url_encode(query))
            self.verification_email_token = token
            self.verification_email_url = url
            # Call Verified Email Template
            template_obj = self.env.ref('base_partner_email_validation.mail_template_verification_res_partner')
            mail_mail_id = template_obj.sudo().with_context(lang=self.lang).send_mail(
                self.id,
                force_send=True,
                raise_exception=True
            )
            # Set True field that indicates if email to confirm has been sent
            if mail_mail_id:
                self.verification_email_sent = True
        except ValidationError:
            pass
