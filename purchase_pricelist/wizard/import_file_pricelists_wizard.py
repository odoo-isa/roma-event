# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from logging import getLogger
import csv
import base64
import io
_logger = getLogger(__name__)


class ImportFilePricelistsWizard(models.TransientModel):
    _name = 'import.file.pricelists.wizard'
    _description = 'Wizard: Import pricelists by csv'

    supplier_id = fields.Many2one(
        string='Supplier',
        required=True,
        readonly=False,
        comodel_name='res.partner'
    )
    pricelist_file = fields.Binary(
        string='CSV File',
        filters='*.csv',
        help="Field that allows to select csv file for import"
    )
    date_start = fields.Date(
        string='Start Date',
        help="Start date for this pricelist"
    )
    date_end = fields.Date(
        string='End Date',
        help="End date for this pricelist"
    )
    family_ids = fields.Many2many(
        string='Families',
        required=False,
        readonly=False,
        comodel_name='supplierinfo.family.wizard',
        relation='import_pricelists_wizard_supplier_family_wizard_rel',
        column1='file_pricelists_wizard_id',
        column2='supplier_family_wizard_id',
        copy=False
    )
    supplier_pricelist_ids = fields.One2many(
        string='Supplier Pricelist',
        required=False,
        readonly=False,
        comodel_name='supplier.pricelist',
        inverse_name='import_file_pricelist_wizard_id',
    )

    @api.onchange('supplier_id')
    def onchange_supplier_id(self):
        self.family_ids = None
        supplier_obj = self.supplier_id
        # Rimuovo le famiglie che non appartengono al fornitore selezionato
        remove_families_obj = self.env['supplierinfo.family.wizard'].search([('supplier_id', '!=', self.supplier_id.id)])
        for remove_family_obj in remove_families_obj:
            remove_family_obj.unlink()
        for supplier_family_obj in supplier_obj.supplier_family_ids:
            vals = {
                'name': supplier_family_obj.name,
                'profit': supplier_family_obj.profit,
                'supplier_id': self.supplier_id.id
            }
            new_supplierinfo_family_wizard_obj = self.env['supplierinfo.family.wizard'].create(vals)
            for discount_obj in supplier_family_obj.discount_ids:
                new_supplierinfo_discount_wizard_obj = self.env['supplierinfo.discount.wizard'].create({
                    'value': discount_obj.value,
                    'label': discount_obj.label,
                    'sequence': discount_obj.sequence
                })
                new_supplierinfo_family_wizard_obj.discount_ids = [(4, new_supplierinfo_discount_wizard_obj.id)]
            self.family_ids = [(4, new_supplierinfo_family_wizard_obj.id)]
        # Salvo i dati che servono al wizard (si perdevano al cambiamento del fornitore)
        self.supplier_id = supplier_obj.id

    def import_data_from_pricelist_file(self):
        """
        Questa funzione permette di leggere i dati relativi al file csv selezionato e li mostra all'utente
        """
        self.ensure_one()
        file = base64.b64decode(self.pricelist_file)  # Decodifico una stringa con codifica Base64
        data = io.StringIO(file.decode("utf-8"))  # Apro il file come testo
        data.seek(0)  # Imposto la posizione corrente del file
        reader = csv.DictReader(data)  # Lettura file csv
        rows = list(reader)
        # Controllo che il formato del file sia di tipo csv
        columns = ['supplier_code', 'description_product', 'supplier_family_name', 'supplier_price', 'fixed_price', 'min_qty', 'profit']
        for column in columns:
            try:
                if column not in rows[0]:
                    raise UserError(_("Selected file isn't a csv format"))
            except ValidationError:
                pass
        # Controllo che già non siano presenti righe lette da listino
        if self.supplier_pricelist_ids:
            self.supplier_pricelist_ids.unlink()
        for row in rows:
            supplier_code = row['supplier_code']
            description_product = row['description_product']
            supplier_family_name = row['supplier_family_name']
            supplier_price = row['supplier_price']
            standard_price = float(supplier_price) if supplier_price else None
            fixed_price = row['fixed_price']
            min_qty = row['min_qty'] if row['min_qty'] else 1.0
            category_discounts = ''
            profit = row['profit']
            category_id = row['category_id'] if 'category_id' in row else None
            if not supplier_price:
                continue
            # FAMILY
            filtered_family_obj = self.family_ids.filtered(
                lambda r: r.name == supplier_family_name
            )
            if not filtered_family_obj:
                # Se non è presente la famiglia tra quelle associate al fornitore, allora applica gli eventuali
                # sconti utilizzando la famiglia di default
                filtered_family_obj = self.family_ids.filtered(
                    lambda f: f.name == '*'
                )
            # PROFIT
            if not profit:
                profit = filtered_family_obj[0].profit  # Profit Family
            # Cerco Supplierinfo per fornitore e codice fornitore
            product_supplierinfo_obj = self.env['product.supplierinfo'].search([
                ('name', '=', self.supplier_id.id),
                ('product_code', '=', supplier_code)
            ])
            if product_supplierinfo_obj:
                template_obj = product_supplierinfo_obj[0].product_tmpl_id
                template_id = template_obj.id
                # Ora filtro il supplierinfo per data iniziale di validità
                supplierinfo_id = product_supplierinfo_obj.filtered(lambda s: s.date_start == self.date_start)
            else:
                supplierinfo_id = None
                template_id = None
            # FIXED PRICE
            if fixed_price:
                standard_price = fixed_price
            else:
                discounts_obj = filtered_family_obj[0].discount_ids.sorted('sequence')
                for discount in discounts_obj:
                    discount_label = ' (' + discount.label + ')' if discount.label else ''
                    category_discounts += '<li>' + str(discount.value) + discount_label + '</li>'
                    discount_value = standard_price * (discount.value / 100)
                    standard_price = standard_price + discount_value
            vals = {
                'supplier_code': supplier_code,
                'description_product': description_product,
                'supplier_family_name': supplier_family_name,
                'supplier_price': supplier_price,
                'standard_price': standard_price,
                'fixed_price': fixed_price,
                'min_qty': min_qty,
                'category_discounts': category_discounts,
                'template_id': template_id,
                'supplierinfo_id': supplierinfo_id[0].id if supplierinfo_id else None,
                'profit': profit if profit else 0.0,
                'category_id': category_id
            }
            new_supplier_pricelist_obj = self.env['supplier.pricelist'].create(vals)
            self.supplier_pricelist_ids = [(4, new_supplier_pricelist_obj.id)]

    def import_pricelist(self):
        """
        Questa funzione legge i dati dal file csv selezionato e visualizza all'utente, le righe prodotti con il costo
        aggiornato da listino
        """
        self.ensure_one()
        # Controllo che tra le Famiglie visualizzate, ci sia almeno una di default per il fornitore selezionato
        exists_default_family = self.family_ids.filtered(lambda f: f.name == '*')
        if not exists_default_family:
            raise ValidationError(_("There isn't default family for the selected supplier. Insert one *"))
        self.import_data_from_pricelist_file()
        view = self.env.ref('purchase_pricelist.wizard_import_file_pricelists_form2')
        return {
            'name': _('Products Preview'),
            "type": "ir.actions.act_window",
            'view_type': 'form',
            'view_mode': 'form',
            "res_model": "import.file.pricelists.wizard",
            "view_id": view.id,
            "res_id": self.id,
            "target": "new"
        }

    def update_products(self):
        """
        Questa funzione permette di creare una riga di prodotto fornitore (product.supplierinfo) con il prezzo da
        listino
        """
        supplier_obj = self.supplier_id
        validity_date_start = self.date_start
        for supplier_pricelist_obj in self.supplier_pricelist_ids:
            # Cerco se già esiste una riga del supplierinfo con inizio data validità uguale a quella scelta
            filtered_supplierinfo_obj = supplier_pricelist_obj.supplierinfo_id
            if filtered_supplierinfo_obj:
                filtered_supplierinfo_obj.with_context(validity_date_end=self.date_end).write({
                    'price': supplier_pricelist_obj.standard_price,
                    'supplier_price': supplier_pricelist_obj.supplier_price,
                    'discounts': supplier_pricelist_obj.category_discounts,
                    'min_qty': supplier_pricelist_obj.min_qty,
                    'profit': supplier_pricelist_obj.profit
                })
                if supplier_pricelist_obj.category_id:
                    supplier_pricelist_obj.template_id.categ_id = supplier_pricelist_obj.category_id
            else:
                template_obj = supplier_pricelist_obj.template_id
                if not template_obj:
                    # Creo nuovo Prodotto e poi una nuova riga del Supplierinfo
                    template_obj = self.env['product.template'].create({
                        'name': supplier_pricelist_obj.description_product,
                        'sale_ok': False,
                        'purchase_ok': False,
                        'default_supplier_id': self.supplier_id.id
                    })
                if supplier_pricelist_obj.category_id:
                    template_obj.categ_id = supplier_pricelist_obj.category_id

                # Creo una nuova riga con la nuova data di validità proveniente del listino e i relativi dati di costo
                self.env['product.supplierinfo'].with_context(validity_date_end=self.date_end).create({
                    'name': supplier_obj.id,
                    'product_code': supplier_pricelist_obj.supplier_code,
                    'price': supplier_pricelist_obj.standard_price,
                    'supplier_price': supplier_pricelist_obj.supplier_price,
                    'discounts': supplier_pricelist_obj.category_discounts,
                    'date_start': validity_date_start,
                    'min_qty': supplier_pricelist_obj.min_qty,
                    'product_tmpl_id': template_obj.id,
                    'profit': supplier_pricelist_obj.profit
                })
        # Aggiorno le Famiglie del Fornitore con quelle inserite dal wizard
        supplier_obj.supplier_family_ids.unlink()  # Elimino le famiglie associate al fornitore selezionato
        for wizard_family_obj in self.family_ids:  # Scorro le famiglie del wizard
            discounts_list = []
            supplier_family_obj = self.env['product.supplier.family'].create({
                'name': wizard_family_obj.name,
                'profit': wizard_family_obj.profit,
                'partner_id': supplier_obj.id
            })
            for discount_obj in wizard_family_obj.discount_ids:  # Scorro gli sconti della famiglia in esame
                new_supplierinfo_discount_obj = self.env['supplierinfo.discount'].create({
                    'value': discount_obj.value,
                    'label': discount_obj.label,
                    'sequence': discount_obj.sequence
                })
                discounts_list.append(new_supplierinfo_discount_obj.id)
            supplier_family_obj.discount_ids = [(6, 0, discounts_list)]

    def turn_back(self):
        """
        Questa funzione permette di ritornare alla schermata precedente del wizard
        """
        view = self.env.ref('purchase_pricelist.wizard_import_file_pricelists_form')
        return {
            'name': _('Products Preview'),
            "type": "ir.actions.act_window",
            'view_type': 'form',
            'view_mode': 'form',
            "res_model": "import.file.pricelists.wizard",
            "view_id": view.id,
            "res_id": self.id,
            "target": "new"
        }
