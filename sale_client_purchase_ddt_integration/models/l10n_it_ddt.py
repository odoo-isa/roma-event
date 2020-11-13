# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class L10nItDdt(models.Model):
    _inherit = "l10n_it.ddt"

    client_purchase_order_ids = fields.Many2many(
        string='Client purchase order',
        comodel_name='client.purchase.order',
        relation='ddt_id_client_purchase_order_id',
        column1='ddt_id',
        column2='client_purchase_order_id',
        help="It indicates list of client purchase order linked to DDT",
        copy=True
    )

    client_purchase_order_required_rel = fields.Boolean(
        string='Client purchase order required',
        related="partner_id.client_purchase_order_required",
        help="It indicates value of flag field in partner who has to use client purchase order",
        copy=False
    )

    @api.constrains('partner_id')
    def _check_client_purchase(self):
        if self.partner_id.client_purchase_order_required and not self.client_purchase_order_ids:
            raise ValidationError(_("Partner requires purchase order in related tab"))

    def action_invoice_create(self, invoice_date, journal_id, final=False):
        res = super(L10nItDdt, self).action_invoice_create(invoice_date, journal_id=journal_id, final=final)
        for record in self:
            for client_purchase_order_id in record.client_purchase_order_ids:
                record.invoice_id.update({
                    'related_document_ids': [(0, 0, {
                        'name': client_purchase_order_id.name,
                        'document_type': 'order',
                        'date': client_purchase_order_id.date
                    })]
                })
        return res

    @api.model
    def create(self, vals):
        # eredito la create del modello dei ddt per valorizzare il buono d'ordine del rispettivo ordine, se c'è
        if self._context.get('active_model', False) == 'sale.order':
            sale_order_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
            vals['client_purchase_order_ids'] = [(6, 0, sale_order_id.mapped('client_purchase_order_ids.id'))]
        return super(L10nItDdt, self).create(vals)

    def write(self, vals):
        for record in self:
            if record._context.get('active_model', False) == 'sale.order':
                sale_order_id = self.env[record._context.get('active_model')].browse(record._context.get('active_id'))
                vals['client_purchase_order_ids'] = []
                for client_purchase_order_id in sale_order_id.client_purchase_order_ids:
                    vals['client_purchase_order_ids'].append((4, client_purchase_order_id.id, 0))
        return super(L10nItDdt, self).write(vals)
