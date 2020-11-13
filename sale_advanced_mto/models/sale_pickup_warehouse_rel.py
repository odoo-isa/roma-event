# -*- coding: utf-8 -*-

from odoo import fields, api, models, _


class SalePickupWarehouseRel(models.Model):
    _name = "sale.pickup.warehouse.rel"
    _description = "Sale Pickup Warehouse Rel"

    warehouse_sale_pickup_id = fields.Many2one(
        string='Stock Warehouse Sale Pickup',
        required=False,
        readonly=False,
        comodel_name='stock.warehouse.sale.pickup',
        ondelete='cascade',
        copy=False
    )
    sequence = fields.Integer(
        string='Sequence',
        required=False,
        readonly=False,
        default=0,
        help="Indicates the sequence useful for sorting warehouses",
        copy=False
    )
    warehouse_id = fields.Many2one(
        string='Warehouse',
        required=True,
        readonly=False,
        comodel_name='stock.warehouse',
        ondelete='cascade',
        copy=False
    )

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        warehouse_sale_pickup_id = self.warehouse_sale_pickup_id
        exclude = []
        if self.env.context.get('warehouse_id', False):
            exclude = [self.env.context.get('warehouse_id')]
        for temporary in warehouse_sale_pickup_id.temporary_warehouse_ids:
            exclude.append(temporary.warehouse_id.id)
        return {
            'domain': {
                'warehouse_id': [('id', 'not in', exclude)]
            }
        }
