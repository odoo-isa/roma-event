# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from logging import getLogger

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    enable_accompanying_invoice = fields.Boolean(
        string='Enable Accompanying Invoice',
        compute='_enable_accompanying_invoice',
        help="Is displayed if exists rows which billing policy (on products) is based by delivery qty and qty "
             "to invoice is positive"
    )

    @api.depends('order_line')
    def _enable_accompanying_invoice(self):
        """
        Questa funzione ritorna True se esistono Righe per cui la politica di fatturazione (sui prodotti) è basata su
        "quantità consegnate" e il campo "qty_to_invoice" risulta essere maggiore di zero.
        In caso positivo sarà visibile il bottone per creare Fatture Accompagnatorie
        """
        for record in self:
            record.enable_accompanying_invoice = False
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            delivered_invoice_policy_line = record.order_line.filtered(
                lambda l: l.product_id.invoice_policy == 'delivery' and float_compare(
                    l.qty_to_invoice, 0.0, precision_digits=precision) > 0
            )
            if delivered_invoice_policy_line:
                record.enable_accompanying_invoice = True

    def create_accompanying_invoice(self):
        self.with_context(accompanying_invoice=True)._create_invoices(final=True)

    def _prepare_invoice(self):
        """
        Se viene creata una Fattura Accompagnatoria nelle vals viene aggiunto il tipo fattura (Accompagnatoria) e le
        relative informazioni di Spedizione reperite dall'Ordine in questione
        """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.env.context.get('accompanying_invoice', False):
            invoice_vals.update({
                'invoice_mode': 'accompanying',
                'goods_description_id': self.goods_description_id.id if self.goods_description_id else None,
                'transportation_reason_id': self.transportation_reason_id.id if self.transportation_reason_id else None,
                'transportation_method_id': self.transportation_method_id.id if self.transportation_method_id else None,
                'invoice_incoterm_id': self.incoterm.id if self.incoterm else None
            })
        return invoice_vals
