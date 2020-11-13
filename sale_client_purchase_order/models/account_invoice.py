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
    def create(self, values):
        res = super(AccountInvoice, self).create(values)
        if res.partner_id.client_purchase_order_required:
            if self._context.get('active_model', False) == 'sale.order' and self._context.get('active_id', False):
                sale_order_id = self.env[self._context.get('active_model', False)].browse(self._context.get('active_id', False))
                for client_purchase_order_id in sale_order_id.client_purchase_order_ids:
                    res.update({
                        'related_document_ids': [(0, 0, {
                            'name': client_purchase_order_id.name,
                            'document_type': 'order',
                            'date': client_purchase_order_id.date
                        })]
                    })
        return res