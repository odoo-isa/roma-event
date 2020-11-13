# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class EmailValidationController(http.Controller):

    @http.route('/web/email/validate', type='http', auth='public', website=True, sitemap=False)
    def web_validate(self, *args, **kw):
        token = kw.get('token')
        partner_id = int(kw.get('id'))
        partner_by_token = request.env['res.partner'].sudo().browse(partner_id)
        partner_lang = partner_by_token.lang
        # Redirect to Error Page
        if token != partner_by_token.verification_email_token or not partner_by_token:
            res = request.render('base_partner_email_validation.not_confirm',
                                 {'company_email': request.env.company.email}
                                 )
            res.set_cookie('frontend_lang', partner_lang)
            return res
        partner_by_token.write({
            'is_verified_email': True,
            'verification_email_token': None,
            'verification_email_url': None
        })
        # Redirect to Successful Confirm Page
        res = request.render('base_partner_email_validation.success_confirm')
        res.set_cookie('frontend_lang', partner_lang)
        return res
