# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from logging import getLogger
from odoo.exceptions import UserError

_logger = getLogger(__name__)


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    supplier_price = fields.Float(
        string='Supplier Price',
        digits='Product Price'
    )
    discounts = fields.Html(
        string='Discounts (%)',
        copy=False
    )
    profit = fields.Float(
        string='Percentage Profit (%)',
        digits='Product Price'
    )
    product_pricelist_item_id = fields.Many2one(
        string='Product Pricelist Item',
        required=False,
        readonly=False,
        comodel_name='product.pricelist.item',
        copy=False
    )

    def _create_item_for_cost_pricelist(self):
        """
        Questa funzione crea una regola per il listino a prezzo di costo
        """
        validity_date_end = self.env.context.get('validity_date_end', False)
        if not validity_date_end:  # Vuol dire che si sta modificando/creando una riga a mano
            validity_date_end = self.date_start  # Data iniziale di acquisto
        profit_value = self.price * (self.profit / 100)
        fixed_price = self.price + profit_value
        template_obj = self.product_tmpl_id
        # Controllo se esiste il riferimento alla riga del listino a prezzo di costo per la supplierinfo in esame
        filtered_product_pricelist_item_obj = self.product_pricelist_item_id
        if filtered_product_pricelist_item_obj:  # Aggiorno Data e Prezzo fisso
            filtered_product_pricelist_item_obj.write({
                'date_start': validity_date_end,
                'fixed_price': fixed_price
            })
        if not filtered_product_pricelist_item_obj and self.company_id.update_sale_pricelist:
            # Listino a prezzo di costo
            cost_pricelist_obj = self.env.ref('purchase_pricelist.cost_pricelist')
            # Cerco se esiste già una regola per quel prodotto e data sul listino a prezzo di costo
            product_pricelist_item_obj = self.env['product.pricelist.item']
            filtered_product_pricelist_item_obj = product_pricelist_item_obj.search([
                ('product_tmpl_id', '=', self.product_tmpl_id.id),
                ('pricelist_id', '=', cost_pricelist_obj.id),
                ('date_start', '=', validity_date_end)
            ])
            if not filtered_product_pricelist_item_obj:
                variant_obj = self.env['product.product'].search([
                    ('name', 'like', template_obj.name),
                    ('product_tmpl_id', '=', template_obj.id)
                ])
                new_item_obj = product_pricelist_item_obj.create({
                    'applied_on': '0_product_variant',
                    'product_tmpl_id': template_obj.id,
                    'product_id': variant_obj.id,
                    'date_start': validity_date_end,
                    'fixed_price': fixed_price,
                    'pricelist_id': cost_pricelist_obj.id
                })
                # Associo la regola listino appena creata alla relativa riga del supplierinfo
                self.write({'product_pricelist_item_id': new_item_obj.id})
            else:
                filtered_product_pricelist_item_obj[0].write({
                    'date_start': validity_date_end,
                    'fixed_price': fixed_price,
                })
        # Aggiorno il prezzo di vendita del prodotto con il prezzo fisso della regola listino
        template_obj.write({'list_price': fixed_price})

    def _default_supplier_row(self):
        # Controllo se la riga in esame appartiene al fornitore abituale
        default_supplier_obj = self.product_tmpl_id.default_supplier_id
        if not default_supplier_obj:
            return False
        if self.name == default_supplier_obj:
            return True
        return False

    @api.model
    def create(self, vals):
        new_supplierinfo_obj = super(ProductSupplierinfo, self).create(vals)
        is_default_supplierinfo_row = new_supplierinfo_obj._default_supplier_row()
        if not is_default_supplierinfo_row:
            return new_supplierinfo_obj
        if 'price' in vals:
            new_supplierinfo_obj._create_item_for_cost_pricelist()
        return new_supplierinfo_obj

    def write(self, values):
        res = super(ProductSupplierinfo, self).write(values)
        is_default_supplierinfo_row = self._default_supplier_row()
        if not is_default_supplierinfo_row:
            return res
        if 'price' in values:
            self._create_item_for_cost_pricelist()
        return res

    def unlink(self):
        if self.product_pricelist_item_id:
            raise UserError(_("You cannot delete this Supplierinfo cause is linked to cost pricelist."))
        return super(ProductSupplierinfo, self).unlink()
