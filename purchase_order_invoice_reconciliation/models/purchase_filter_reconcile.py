# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, tools
from odoo.osv import expression
from odoo.tools import formatLang, format_date
from logging import getLogger

_logger = getLogger(__name__)


class PurchaseFilterReconcile(models.Model):
    _name = 'purchase.filter.reconcile'
    _auto = False
    _description = 'Purchase used for filter in reconcile'

    name = fields.Char(
        string='Purchase order name',
        readonly=True
    )

    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name="res.partner",
        readonly=True
    )

    partner_ref = fields.Char(
        string='Reference',
        readonly=True
    )

    internal_reference = fields.Char(
        string='Internal reference',
        readonly=True
    )

    date_order = fields.Date(
        string='Order date',
        readonly=True
    )

    amount = fields.Float(
        string='Amount',
        readonly=True
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        readonly=True
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'purchase_filter_reconcile')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW purchase_filter_reconcile AS (
                SELECT 
                    id, "name", partner_id as supplier_id, partner_ref, internal_reference, date_order, amount_untaxed as amount, currency_id 
                FROM 
                    purchase_order
                WHERE 
                    state in ('purchase', 'done') AND
                    invoice_status = 'to invoice'
            )
        """)

    def name_get(self):
        result = []
        for doc in self:
            name_model = list()
            name_model.append("%s(%s %s)" % (
                doc.name,
                format_date(self.env, doc.date_order),
                formatLang(self.env, doc.amount, monetary=True, currency_obj=doc.currency_id)
            ))
            if doc.partner_ref:
                name_model.append("Ref.%s" % doc.partner_ref)
            if doc.internal_reference:
                name_model.append("Int.Ref.%s" % doc.internal_reference)
            name_get = '/'.join(name_model)
            result.append((doc.id, name_get))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        # OR search
        or_args = []
        # Search for name
        or_args = expression.OR([or_args, [('name', 'ilike', name)]])
        # Search for partner_ref
        or_args = expression.OR([or_args, [('partner_ref', 'ilike', name)]])
        # Search for internal reference
        or_args = expression.OR([or_args, [('internal_reference', 'ilike', name)]])
        # Perform search XAND -> OR
        args = expression.AND([args, or_args])
        purchase_filter = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(purchase_filter).with_user(name_get_uid))
