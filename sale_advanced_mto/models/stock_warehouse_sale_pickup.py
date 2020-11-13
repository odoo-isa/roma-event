# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockWarehouseSalePickup(models.Model):
    _name = "stock.warehouse.sale.pickup"
    _description = "Stock Warehouse Sale Pickup"
    _rec_name = 'full_path_name'

    full_path_name = fields.Char(
        compute='_get_full_path_name',
        string='Path'
    )
    warehouse_id = fields.Many2one(
        string='Warehouse',
        required=False,
        readonly=False,
        comodel_name='stock.warehouse',
        ondelete='cascade',
        copy=False
    )
    temporary_warehouse_ids = fields.One2many(
        string='Temporary Warehouses',
        required=False,
        readonly=False,
        comodel_name='sale.pickup.warehouse.rel',
        inverse_name='warehouse_sale_pickup_id',
        help="Indicates the warehouses from which the goods must pass",
        copy=False
    )

    @api.depends('temporary_warehouse_ids')
    def _get_full_path_name(self):
        for record in self:
            warehouses_name = []
            ordered_temporary_warehouse = self.env['sale.pickup.warehouse.rel'].search([(
                'warehouse_sale_pickup_id', '=', record.id
            )], order="sequence, id")
            for temporary_warehouse in ordered_temporary_warehouse:
                warehouses_name.append(temporary_warehouse.warehouse_id.code)
            sale_pickup_name = ' → '.join(warehouses_name)
            record.full_path_name = sale_pickup_name
