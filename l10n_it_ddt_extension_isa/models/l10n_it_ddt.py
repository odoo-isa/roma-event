# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import format_date, float_is_zero
from logging import getLogger
import collections

_logger = getLogger(__name__)


class L10nItDdt(models.Model):
    _name = 'l10n_it.ddt'
    _inherit = ['l10n_it.ddt', 'mail.thread', 'mail.activity.mixin']

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('l10n_it.ddt')

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.model
    def _default_incoterm(self):
        return self.env.user.company_id.incoterm_id

    name = fields.Char(
        required=False,
        readonly=True,
    )

    currency_id = fields.Many2one(
        string='Currency',
        required=True,
        comodel_name='res.currency',
        states={'draft': [('readonly', False)]},
        default=_default_currency,
        track_visibility='always'
    )

    date = fields.Date(
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    l10n_it_ddt_sequence = fields.Many2one(
        string='Sequence',
        required=True,
        default=lambda self: self.env.ref('l10n_it_ddt_extension_isa.seq_ddt', raise_if_not_found=False),
        comodel_name='ir.sequence',
        ondelete='restrict',
        help='''The sequence used for retrieve the correct sequential DDT number.''',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    partner_type = fields.Selection(
        string='Partner type',
        required=True,
        default='customer',
        selection=[
            ('customer', 'Customer'),
            ('supplier', 'Supplier'),
            ('internal', 'Internal')
        ],
        help="""Type of partner (customer, supplier or internal)""",
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    partner_id = fields.Many2one(
        string='Partner',
        required=True,
        ondelete='restrict',
        comodel_name='res.partner',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    partner_shipping_id = fields.Many2one(
        string='Delivery Address',
        help="Delivery address for current DdT.",
        comodel_name='res.partner',
        ondelete="restrict",
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    ddt_lines = fields.One2many(
        string='Ddt Line',
        comodel_name='l10n_it.ddt.line',
        inverse_name='l10n_it_ddt_id',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    goods_description_id = fields.Many2one(
        string='Description of Goods',
        comodel_name='l10n_it.goods_description',
        ondelete='restrict',
        help='This field indicates the appearance of the goods',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    transportation_reason_id = fields.Many2one(
        string='Reason for Transportation',
        comodel_name='l10n_it.transportation_reason',
        ondelete='restrict',
        help='Reason for Transportation',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    transportation_method_id = fields.Many2one(
        string='Transportation Method',
        comodel_name='l10n_it.transportation_method',
        ondelete='restrict',
        help='Method of Transportation',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    parcels = fields.Integer(
        string='Parcels',
        help='Number of parcels related with the shipping',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    note = fields.Text(
        string='Note',
    )

    state = fields.Selection(
        string='State',
        default='draft',
        help='State of Ddt',
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
            ('invoiced', 'Invoiced')
        ],
        track_visibility='onchange',
    )

    weight = fields.Float(
        string='Weight',
        default=0.0,
        copy=False,
        digits='Stock Weight',
        help="The Weight in Kg.",
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    weight_net = fields.Float(
        string='Weight Net',
        default=0.0,
        copy=False,
        digits='Stock Weight',
        help="The Net weight in Kg.",
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    date_done = fields.Datetime(
        string='Date Done',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        ondelete='restrict',
        index=True,
        default=_default_company,
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    incoterm_id = fields.Many2one(
        string='Incoterm',
        help='International Commercial Terms are a series of predefined '
             'commercial terms used in international transactions.',
        comodel_name='account.incoterms',
        ondelete='restrict',
        default=_default_incoterm,
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    invoice_option = fields.Selection(
        string='Invoice option',
        default='billable',
        required=True,
        selection=[('billable', 'Billable'), ('non-billable', 'Non-billable')],
        help="Indicate if DdT is billable or not",
        track_visibility='onchange',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    invoice_id = fields.Many2one(
        string='Invoice',
        help="Invoice generated by the DDT",
        comodel_name='account.move',
        ondelete='set null',
    )

    payment_term_id = fields.Many2one(
        string='Payment Term',
        comodel_name='account.payment.term',
        ondelete='restrict',
        states={
            'confirmed': [('readonly', True)],
            'cancelled': [('readonly', True)],
            'invoiced': [('readonly', True)]
        }
    )

    amount_untaxed = fields.Monetary(
        string='Untaxed Amount',
        store=True,
        readonly=True,
        compute='_compute_amount',
        track_visibility='always',
    )

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        self.partner_id = None
        self.partner_shipping_id = None
        self.payment_term_id = None
        self.goods_description_id = None
        self.transportation_reason_id = None
        self.transportation_method_id = None
        self.ddt_lines = None
        if self.partner_type == 'customer':
            self.invoice_option = 'billable'
        elif self.partner_type == 'supplier':
            self.invoice_option = 'non-billable'
        else:
            self.invoice_option = 'non-billable'
        return {
            'domain': {
                'partner_shipping_id': [('id', 'in', [])]
            }
        }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.goods_description_id = self.partner_id.goods_description_id.id
            self.transportation_reason_id = self.partner_id.transportation_reason_id.id
            self.transportation_method_id = self.partner_id.transportation_method_id.id
            self.payment_term_id = self.partner_id.property_payment_term_id.id
            if self.partner_id.parent_id:
                partner_obj = self.partner_id.parent_id
            else:
                partner_obj = self.partner_id
            self.partner_shipping_id = partner_obj.id
            shipping_contact = partner_obj.child_ids.filtered(lambda c: c.type == 'delivery')
            partner_obj += shipping_contact
            return {
                'domain': {
                    'partner_shipping_id': [('id', 'in', partner_obj.ids)]
                }
            }

    @api.model
    def create(self, vals):
        if vals['partner_type'] in ['supplier', 'internal']:
            vals['invoice_option'] = 'non-billable'
        return super(L10nItDdt, self).create(vals)

    def write(self, vals):
        res = True
        for record in self:
            if 'partner_type' in vals and vals['partner_type'] in ['supplier', 'internal']:
                vals['invoice_option'] = 'non-billable'
            res |= super(L10nItDdt, record).write(vals)
        return res

    def name_get(self):
        res = []
        for ddt in self:
            if ddt.name:
                ddt_name = "%s (%s)" % (ddt.name, format_date(self.env, ddt.date))
            else:
                ddt_name = "DdT (*%s) %s" % (ddt.id, format_date(self.env, ddt.date))
            res.append((ddt.id, ddt_name))
        return res

    def set_to_draft(self):
        for ddt in self:
            ddt.state = "draft"

    def set_to_invoiced(self):
        for ddt in self:
            ddt.state = "invoiced"

    def set_to_cancelled(self):
        for ddt in self:
            ddt.state = "cancelled"

    def confirm_ddt(self):
        for record in self:
            # DdT must have at least one line
            if not record.ddt_lines:
                raise ValidationError(
                    _("Unable to confirm a DdT that don't have lines.")
                )
            sequence = record.l10n_it_ddt_sequence
            if not sequence:
                raise ValidationError(
                    _("There isn't a sequence specified for this DDT. Please provided one.")
                )
            if not record.date_done:
                record.date_done = fields.datetime.now()
            if not record.name:
                record.name = sequence.with_context(
                    ir_sequence_date=record.date,
                    ir_sequence_date_range=record.date
                ).next_by_id()
            record.state = 'confirmed'

    @api.depends('ddt_lines.price_subtotal', 'ddt_lines.product_id.taxes_id', 'currency_id', 'company_id')
    def _compute_amount(self):
        for record in self:
            amount_untaxed = sum(line.price_subtotal for line in record.ddt_lines)
            if record.currency_id and record.company_id and record.currency_id != record.company_id.currency_id:
                currency_id = record.currency_id
                amount_untaxed = currency_id._convert(
                    record.amount_untaxed,
                    record.company_id.currency_id,
                    record.company_id,
                    record.date or fields.Date.today()
                )
            record.amount_untaxed = amount_untaxed

    @api.depends('state')
    def _compute_ddt_name(self):
        if not self.env.user._is_system():
            return
        for record in self:
            if record.state == 'confirmed':
                sequence = record.l10n_it_ddt_sequence
                if not sequence:
                    raise ValidationError(
                        _("There isn't a sequence specified for this DDT. Please provided one.")
                    )
                record.name = sequence.with_context(
                    ir_sequence_date=record.date,
                    ir_sequence_date_range=record.date
                ).next_by_id()

    # Methods for invoicing DDT
    def invoice_preliminary_check(self, date_invoice):
        """
        This method return a dictionary of dictionary grouped for code.
        The second dictionary contains a list of ddt whit relative error.
        :param date_invoice:
        :return: Dictionary grouped of code whit Error and list of Ddt
        """
        ddt_not_to_invoice = {}
        for record in self:
            if record.invoice_id:
                err_dict = ddt_not_to_invoice.setdefault('001', {
                    'desc': _('This DdT are already invoiced: '), 'ddt': []
                })
                err_dict['ddt'].append(record)
                continue
            if record.state != 'confirmed':
                err_dict = ddt_not_to_invoice.setdefault('002', {
                    'desc': _('This DdT are not in Confirmed state: '), 'ddt': []
                })
                err_dict['ddt'].append(record)
                continue
            if record.date > date_invoice:
                err_dict = ddt_not_to_invoice.setdefault('004', {
                    'desc': _('Date of the invoice is previous to that of the DdT: '), 'ddt': []
                })
                err_dict['ddt'].append(record)
                continue
        return ddt_not_to_invoice

    def action_invoice_create(self, invoice_date, journal_id=False, final=False):
        """
            Create the invoice associated to the Ddt.
            :param final: if True, refunds will be generated if necessary
            :returns: list of created invoices
                """
        inv_obj = self.env['account.move']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}
        created_invoices = self.env['account.move']
        # Keep track of the sequences of the lines
        # To keep lines under their section
        inv_line_sequence = 0
        for ddt in self:
            tuple_field = ddt.get_grouped_field_name()
            tuple_value = ddt.get_grouped_field_value(journal_id)
            tuple_structure = collections.namedtuple('key', tuple_field)
            group_key = tuple_structure(**tuple_value)
            # Create lines in batch to avoid performance problems
            line_vals_list = []
            invoice = self.env['account.move']
            # Loop thought ddt lines
            for num_line, line in enumerate(ddt.ddt_lines, 1):
                qty_to_invoice = line._compute_quantity_to_invoice(precision)
                if float_is_zero(qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = ddt._prepare_invoice(invoice_date, group_key)
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = ddt
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.invoice_origin]
                    invoices_name[group_key] = [invoice.name]
                else:
                    invoice = invoices[group_key]
                    if ddt.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(ddt.name)
                    if invoice.partner_shipping_id != ddt.partner_shipping_id:
                        invoice.partner_shipping_id = None
                if qty_to_invoice > 0 or (qty_to_invoice < 0 and final):
                    inv_line_sequence += 1
                    inv_line = line.with_context(journal_id=journal_id.id, type='out_invoice').invoice_line_create_vals(
                        invoices[group_key].id, qty_to_invoice, num_line
                    )
                    inv_line[0]['sequence'] = inv_line_sequence
                    line_vals_list.extend(inv_line)
            if invoice:
                invoice.write({
                    'related_document_ids': [(0, 0, {
                                                'document_type': 'ddt',
                                                'name': ddt.name,
                                                'date': ddt.date
                                            })]
                })
            ddt.invoice_id = invoice
            ddt.state = 'invoiced'
            ddt._add_extra_line(line_vals_list, invoices[group_key].id)
            if references.get(invoices.get(group_key)):
                if ddt not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= ddt
            self.env['account.move.line'].with_context(check_move_validity=False).create(line_vals_list)
            if not invoice in created_invoices:
                created_invoices += invoice
        # The first step is to recalculate the lines of the accounting records, without checking any unbalances. After
        # the registration is complete I repeat the recalculation with the check of the balance.
        created_invoices.with_context(check_move_validity=False)._recompute_dynamic_lines(
            recompute_all_taxes=True,
            recompute_tax_base_amount=True
        )
        created_invoices._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
        if not invoices:
            raise UserError(
                _('There is no lines that can be invoiced.')
            )

        for group_key in invoices:
            invoices[group_key].write({
                'invoice_origin': ', '.join(invoices_origin[group_key]),
                'ref': ', '.join(invoices_origin[group_key])
            })
            ddt_ids = references[invoices[group_key]]
            # Invoice all delivery expense
            invoices[group_key]._compute_delivery_expense(precision)

        self.env['account.move'].with_context(set_partner_shipping=True).post_create(invoices, references)
        return [inv.id for inv in invoices.values()]

    def get_grouped_field_name(self) -> list:
        field_name = [
            'partner_id',
            'company_id',
            'currency_id',
            'payment_term_id',
            'transportation_reason_id',
            'journal_id'
        ]
        return field_name

    def get_grouped_field_value(self, journal_id=None) -> dict:
        field_value = {
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'payment_term_id': self.payment_term_id.id,
            'transportation_reason_id': self.transportation_reason_id.id,
            'journal_id': journal_id.id
        }
        return field_value

    def _add_extra_line(self, line_vals_list, move_id):
        pass

    def _prepare_invoice(self, invoice_date, group_key):
        """
        Prepare the dict of values to create the new invoice for a Ddt. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        invoice_vals = {
            'invoice_origin': self.name,
            'type': 'out_invoice',
            'invoice_mode': 'deferred',
            'partner_id': group_key.partner_id,
            'journal_id': group_key.journal_id,
            'currency_id': group_key.currency_id,
            'narration': self.note,
            'invoice_payment_term_id': group_key.payment_term_id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'company_id': group_key.company_id,
            'invoice_date': invoice_date,
            'invoice_incoterm_id': self.incoterm_id.id,
            'partner_shipping_id': self.partner_shipping_id.id
        }
        return invoice_vals

    def action_view_invoice_from_ddt(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[self.env.ref('account.view_move_form').id, "form"]],
            "res_id": self.invoice_id.id
        }

    def action_view_invoice(self, invoices):
        """ This method return view of Ddt.
        :param invoices:
        :return: view of ddt.
        """
        action = self.env.ref('account.action_move_line_form').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def unlink(self):
        if self.filtered(lambda d: d.state not in ['draft', 'cancelled']):
            raise ValidationError(_("It's possible delete a DdT only in the Draft or Cancelled state"))
        return super(L10nItDdt, self).unlink()
