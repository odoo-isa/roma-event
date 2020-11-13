# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from logging import getLogger

_logger = getLogger(__name__)


class L10nItDdtLine(models.Model):
    _name = 'l10n_it.ddt.line'
    _description = 'DDT Line'
    _rec_name = 'description'

    l10n_it_ddt_id = fields.Many2one(
        string='DDT',
        required=True,
        comodel_name='l10n_it.ddt',
        ondelete="cascade",
    )

    state = fields.Selection(
        name="State",
        related="l10n_it_ddt_id.state"
    )

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        domain=[('type', '=', 'consu')],
        context={
            'default_type': 'consu'
        },
        ondelete='restrict',
    )

    description = fields.Text(
        string='Description',
        required=True,
    )

    quantity = fields.Float(
        string='Quantity',
        index=False,
        default=1.0,
        required=True,
        digits='Product Unit of Measure',
    )

    uom_id = fields.Many2one(
        string='Unit of measure',
        comodel_name='uom.uom',
        ondelete='restrict',
    )

    ddt_line_tax_ids = fields.Many2many(
        string='Taxes',
        comodel_name='account.tax',
        relation='ddt_line_tax_rel',
        column1='ddt_line_id',
        column2='tax_id',
    )

    type_tax_use = fields.Char(
        string='Type tax use',
        help="Technical field",
        compute="_compute_type_tax_use"
    )

    price_unit = fields.Float(
        string='Unit Price',
        digits='Product Price',
        help="Price unit",
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='l10n_it_ddt_id.currency_id',
        store=True,
        related_sudo=False,
        readonly=False
    )

    price_subtotal = fields.Monetary(
        string='Amount (without Taxes)',
        store=True,
        readonly=True,
        compute="_compute_price",
        help="Total amount without taxes"
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        partner_type = self.l10n_it_ddt_id.partner_type
        # From product retrieve...
        if partner_type == 'customer':
            uom_id = self.product_id.uom_id.id
            product_price_unit = self.product_id.lst_price
            taxes = self.product_id.taxes_id
        else:
            uom_id = self.product_id.uom_po_id.id
            product_price_unit = self.product_id.standard_price
            taxes = self.product_id.supplier_taxes_id
        # Description
        self.description = self.product_id.name
        self.ddt_line_tax_ids = taxes
        # Uom
        if not self.uom_id:
            self.uom_id = uom_id
        # Price unit
        self.price_unit = product_price_unit
        company = self.l10n_it_ddt_id.company_id
        currency = self.l10n_it_ddt_id.currency_id
        if company and currency:
            if self.uom_id and self.uom_id.id != self.product_id.uom_id.id:
                self.price_unit = self.product_id.uom_id._compute_price(self.price_unit, self.uom_id)

    @api.depends('price_unit', 'ddt_line_tax_ids', 'quantity',
                 'product_id', 'l10n_it_ddt_id.partner_id', 'l10n_it_ddt_id.currency_id', 'l10n_it_ddt_id.company_id',
                 'l10n_it_ddt_id.date_done')
    def _compute_price(self):
        for record in self:
            currency = record.l10n_it_ddt_id.currency_id
            price = record.price_unit
            taxes = False
            if record.ddt_line_tax_ids:
                taxes = record.ddt_line_tax_ids.compute_all(
                    price,
                    currency,
                    record.quantity,
                    product=record.product_id,
                    partner=record.l10n_it_ddt_id.partner_id
                )
            record.price_subtotal = taxes['total_excluded'] if taxes else record.quantity * price
            if record.l10n_it_ddt_id.currency_id and record.l10n_it_ddt_id.currency_id != record.l10n_it_ddt_id.company_id.currency_id:
                currency = record.l10n_it_ddt_id.currency_id
                record.price_subtotal = currency._convert(
                    record.price_subtotal,
                    record.l10n_it_ddt_id.company_id.currency_id,
                    record.l10n_it_ddt_id.company_id or self.env.user.company_id,
                    record.l10n_it_ddt_id.date_done or fields.Date.today())

    @api.depends('l10n_it_ddt_id.partner_type')
    def _compute_type_tax_use(self):
        for record in self:
            record.type_tax_use = 'sale' if record.l10n_it_ddt_id.partner_type == 'customer' else 'purchase'
            
    @api.onchange('ddt_line_tax_ids')
    def _onchange_ddt_line_tax(self):
        type_tax_use = 'sale' if self.l10n_it_ddt_id.partner_type == 'customer' else 'purchase'
        return {
            'domain': {
                'ddt_line_tax_ids': [('type_tax_use', '=', type_tax_use)]
            }
        }
        
    @api.model
    def _compute_quantity_to_invoice(self, precision):
        """
        Inherited function to determinate the quantity to invoice
        :param precision: the precision digits
        :return: quntity to invoice (float)
        """
        return self.quantity

    @api.model
    def invoice_line_create_vals(self, invoice_id, qty, num_line=0):
        """ Create an invoice line. The quantity to invoice can be positive (invoice) or negative
            (refund).
            :param invoice_id: integer
            :param qty: float quantity to invoice
            :returns list of dict containing creation values for account.move.line records
        """
        vals_list = []
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision) or not line.product_id:
                vals = line._prepare_invoice_line(qty, num_line)
                vals.update({
                    'move_id': invoice_id
                })
                vals_list.append(vals)
        return vals_list

    def _prepare_invoice_line(self, qty, num_line=0):
        """
        Prepare the dict of values to create the new invoice line for a ddt line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            account = self.env['account.move.line'].with_context(default_type=self._context['type']).default_get(['account_id'])
            account = self.env['account.account'].browse(account.get('account_id', False))

        if not account and self.product_id:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.l10n_it_ddt_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        res = {
            'name': self.description,
            'ref': self.l10n_it_ddt_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'product_uom_id': self.uom_id.id,
            'product_id': self.product_id.id or False,
            'tax_ids': [(6, 0, self.ddt_line_tax_ids.ids)],
            'ddt_id': self.l10n_it_ddt_id.id,
            'ddt_line_id': self.id,
            'related_document_line_ids': [(0, 0, {
                'document_type': 'ddt',
                'name': self.l10n_it_ddt_id.name,
                'line_ref': num_line,
                'date': self.l10n_it_ddt_id.date
            })]
        }
        return res

