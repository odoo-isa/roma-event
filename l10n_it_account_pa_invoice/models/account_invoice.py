# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.model
    def create(self, vals):
        # eredito la funzione per aggiungere un documento correlato preso da CIG e CUP nell'indirizzo di consegna, se ci sono
        res = super(AccountInvoice, self).create(vals)
        if 'partner_shipping_id' in vals and (res.partner_shipping_id.cig or res.partner_shipping_id.cup):
            name = res.partner_shipping_id.cig or res.partner_shipping_id.cup or False
            res.related_document_ids = [(0, 0, {
                'document_type': 'contract',
                'name': name,
                'date': res.invoice_date,
                'cig': res.partner_shipping_id.cig,
                'cup': res.partner_shipping_id.cup
            })]
        return res

    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        for record in self:
            if 'partner_shipping_id' in vals:
                record.related_document_ids.filtered(
                    lambda d: d.document_type == 'contract' and (d.cig or d.cup)
                ).unlink()
                if record.partner_shipping_id.cig or record.partner_shipping_id.cup:
                    name = record.partner_shipping_id.cig or record.partner_shipping_id.cup or False
                    record.related_document_ids = [(0, 0, {
                        'document_type': 'contract',
                        'name': name,
                        'date': record.invoice_date,
                        'cig': record.partner_shipping_id.cig,
                        'cup': record.partner_shipping_id.cup
                    })]
        return res
