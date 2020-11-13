# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, _
from logging import getLogger

_logger = getLogger(__name__)


class SupplierPricelist(models.TransientModel):
    _name = 'supplier.pricelist'
    _description = 'Supplier Pricelist'

    import_file_pricelist_wizard_id = fields.Many2one(
        string='Import Pricelist Wizard',
        required=False,
        readonly=False,
        comodel_name='import.file.pricelists.wizard'
    )
    supplier_code = fields.Char(
        string='Supplier code'
    )
    description_product = fields.Char(
        string='Description Product'
    )
    supplier_family_name = fields.Char(
        string='Family'
    )
    product_category_id = fields.Many2one(
        string='Product Category',
        required=False,
        readonly=False,
        comodel_name='product.category',
        ondelete='cascade',
        copy=False
    )
    supplier_price = fields.Float(
        string='Supplier Price',
        digits='Product Price'
    )
    standard_price = fields.Float(
        string='Cost',
        digits='Product Price'
    )
    fixed_price = fields.Boolean(
        string='Fixed Price'
    )
    category_discounts = fields.Html(
        string='Category Discounts'
    )
    min_qty = fields.Float(
        string='Quantity'
    )
    template_id = fields.Many2one(
        string='Template',
        required=False,
        readonly=False,
        comodel_name='product.template',
        help="It's used to know if is a new rule to be imported: Red means that a template for the rule in question "
             "has not been found, then the template is automatically created and then the rule"
    )
    supplierinfo_id = fields.Many2one(
        string='Supplierinfo',
        required=False,
        readonly=False,
        comodel_name='product.supplierinfo'
    )
    profit = fields.Float(
        string='Percentage Profit (%)',
        required=False,
        readonly=False,
        default=0.0,
        digits='Product Price'
    )

    category_id = fields.Many2one(
        string='Category',
        comodel_name='product.category',
        help="",
        copy=False
    )
