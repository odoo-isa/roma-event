# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo import SUPERUSER_ID
from odoo.osv import expression
from logging import getLogger
from psycopg2 import IntegrityError
_logger = getLogger("Management Warehouses")


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    sale_buy_behalf_ids = fields.Many2many(
        string='Buy behalf',
        required=False,
        readonly=False,
        comodel_name='stock.warehouse',
        relation='stock_wh_sale_buy_behalf_rel',
        column1='buyer_wh_id',
        column2='bought_wh_id',
        help="Routes will be automatically created to buy from this warehouse to the selected warehouses",
        copy=False
    )
    sale_buy_receving_in_ids = fields.Many2many(
        string='Buy receving in',
        required=False,
        readonly=False,
        comodel_name='stock.warehouse',
        relation='stock_wh_sale_buy_receving_rel',
        column1='bought_wh_id',
        column2='buyer_wh_id',
        help="Routes will be automatically created to sell from this warehouse to the selected warehouses",
        copy=False
    )
    sale_pick_up_from_ids = fields.One2many(
        string='Pick-up from',
        required=False,
        readonly=False,
        comodel_name='stock.warehouse.sale.pickup',
        inverse_name='warehouse_id',
        help="Indicate the paths that goods must take to get to the warehouse",
        copy=False
    )
    wh_transit_stock_loc_id = fields.Many2one(
        string='Transit Location',
        comodel_name='stock.location',
        check_company=True,
        ondelete='restrict'
    )
    shipment_sale_type_id = fields.Many2one(
        string='Shipment Sale Type (Other warehouse)',
        required=False,
        readonly=False,
        comodel_name='stock.picking.type',
        check_company=True
    )
    receipt_sale_type_id = fields.Many2one(
        string='Receipt Sale Type (Other warehouse)',
        required=False,
        readonly=False,
        comodel_name='stock.picking.type',
        check_company=True
    )

    def _get_locations_values(self, vals, code=False):
        """
        Create transit location's warehouse
        """
        res = super(StockWarehouse, self)._get_locations_values(vals, code)
        code = vals.get('code') or code or ''
        code = code.replace(' ', '').upper()
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        res.update({
            'wh_transit_stock_loc_id': {
                'name': _('Transit'),
                'active': True,
                'usage': 'transit',
                'barcode': self._valid_barcode(code + '-TRANSIT', company_id)
            }
        })
        return res

    def _format_rulename(self, from_loc, dest_loc, suffix):
        """
        Odoo doesn't perform checks if the source location is empty, for this reason the function was inherited
        """
        if not from_loc:
            rulename = '%s: ' % self.code
            if dest_loc:
                rulename += '%s → %s' % (from_loc.display_name, dest_loc.display_name)
            if suffix:
                rulename += ' (' + suffix + ')'
            return rulename
        else:
            return super(StockWarehouse, self)._format_rulename(from_loc, dest_loc, suffix)

    def _get_rule_values(self, route_values, values=None, name_suffix=''):
        """
        This function has been rewritten to add control for the destination source when is empty
        (useful for buy type rules)
        """
        first_rule = True
        rules_list = []
        for routing in route_values:
            from_loc_id = routing.from_loc.id if routing.from_loc else False
            route_rule_values = {
                'name': self._format_rulename(routing.from_loc, routing.dest_loc, name_suffix),
                'location_src_id': from_loc_id,
                'location_id': routing.dest_loc.id,
                'action': routing.action,
                'auto': 'manual',
                'picking_type_id': routing.picking_type.id,
                'procure_method': first_rule and 'make_to_stock' or 'make_to_order',
                'warehouse_id': self.id,
                'company_id': self.company_id.id,
                'delay_alert': routing.picking_type.code == 'outgoing',
            }
            route_rule_values.update(values or {})
            rules_list.append(route_rule_values)
            first_rule = False
        if values and values.get('propagate_cancel') and rules_list:
            # In case of rules chain with cancel propagation set, we need to stop
            # the cancellation for the last step in order to avoid cancelling
            # any other move after the chain.
            # Example: In the following flow:
            # Input -> Quality check -> Stock -> Customer
            # We want that cancelling I->GC cancel QC -> S but not S -> C
            # which means:
            # Input -> Quality check should have propagate_cancel = True
            # Quality check -> Stock should have propagate_cancel = False
            rules_list[-1]['propagate_cancel'] = False
        return rules_list

    def _get_sequence_values(self):
        res = super(StockWarehouse, self)._get_sequence_values()
        res.update({
            'shipment_sale_type_id': {
                'name': self.name + ' ' + _('Sequence sold shipment'),
                'prefix': self.code + '/OUT/SOLD/',
                'padding': 5,
                'company_id': self.company_id.id
            },
            'receipt_sale_type_id': {
                'name': self.name + ' ' + _('Sequence sold receipt'),
                'prefix': self.code + '/IN/SOLD/',
                'padding': 5,
                'company_id': self.company_id.id
            }
        })
        return res

    def _get_picking_type_update_values(self):
        res = super(StockWarehouse, self)._get_picking_type_update_values()
        input_loc, output_loc = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        res.update({
            'shipment_sale_type_id':
                {
                    'default_location_src_id': output_loc.id,
                    'active': self._is_active_receipt_ship_sale_picking_type()
                },
            'receipt_sale_type_id':
                {
                    'default_location_dest_id': input_loc.id,
                    'active': self._is_active_receipt_ship_sale_picking_type()
                }
        })
        return res

    def _get_picking_type_create_values(self, max_sequence):
        res, max_sequence = super(StockWarehouse, self)._get_picking_type_create_values(max_sequence)
        res.update({
            'shipment_sale_type_id': {
                'name': _('Shipments for Sold'),
                'code': 'outgoing',
                'use_create_lots': False,
                'use_existing_lots': True,
                'default_location_dest_id': False,
                'sequence': max_sequence + 1,
                'barcode': self.code.replace(" ", "").upper() + "-SHIPMENT_SALE",
                'sequence_code': self.code + 'OUT/SOLD/',
                'company_id': self.company_id.id,
                'active': self._is_active_receipt_ship_sale_picking_type()
            },
            'receipt_sale_type_id': {
                'name': _('Receipts for Sold'),
                'code': 'incoming',
                'use_create_lots': True,
                'use_existing_lots': False,
                'default_location_src_id': False,
                'sequence': max_sequence + 2,
                'barcode': self.code.replace(" ", "").upper() + "-RECEIPTS_SALE",
                'show_reserved': False,
                'sequence_code': self.code + 'IN/SOLD/',
                'company_id': self.company_id.id,
                'active': self._is_active_receipt_ship_sale_picking_type()
            }
        })
        return res, max_sequence+3

    def _create_or_update_sequences_and_picking_types(self):
        res = super(StockWarehouse, self)._create_or_update_sequences_and_picking_types()
        if 'shipment_sale_type_id' in res:
            self.env['stock.picking.type'].browse(res['shipment_sale_type_id']).write({
                'return_picking_type_id': res.get('receipt_sale_type_id', False)
            })
        if 'receipt_sale_type_id' in res:
            self.env['stock.picking.type'].browse(res['receipt_sale_type_id']).write({
                'return_picking_type_id': res.get('shipment_sale_type_id', False)
            })
        return res

    def _check_external_reference_sequence(self, type_picking):
        """
        This function is used to retrieve external reference's object
        :params type_picking: String (shipment/receipt)
        """
        if type_picking == 'shipment':
            prefix = self.code + 'OUT/SOLD/'
        elif type_picking == 'receipt':
            prefix = self.code + 'IN/SOLD/'
        else:
            raise ValidationError(f"Invalid type_picking. Expected shipment or receipt get {type_picking}")
        sequence_obj = self.env['ir.sequence'].create({
            'name': self.name + ' ' + _('Sequence sold %s' % type_picking),
            'prefix': prefix,
            'padding': 5,
            'company_id': self.company_id.id,
        })
        return sequence_obj

    def _create_shipment_picking_type(self):
        """
        This function allows to create shipment picking type
        """
        __, location_out = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        active = self._is_active_receipt_ship_sale_picking_type()
        sequence = self._check_external_reference_sequence('shipment')
        shipment_picking_type_obj = self.env['stock.picking.type'].create({
            'name': _('Shipments for Sold'),
            'code': 'outgoing',
            'use_create_lots': False,
            'use_existing_lots': True,
            'default_location_src_id': location_out.id,
            'default_location_dest_id': False,
            'barcode': self.code.replace(" ", "").upper() + "-SHIPMENT_SALE",
            'warehouse_id': self.id,
            'sequence_code': sequence.prefix,
            'sequence_id': sequence.id,
            'company_id': self.company_id.id,
            'active': active
        })
        self.write({'shipment_sale_type_id': shipment_picking_type_obj.id})

    def _create_receipt_picking_type(self):
        """
        This function allows to create receipt picking type
        """
        location_in, __ = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        active = self._is_active_receipt_ship_sale_picking_type()
        sequence = self._check_external_reference_sequence('receipt')
        receipt_sale_type_obj = self.env['stock.picking.type'].create({
            'name': _('Receipts for Sold'),
            'code': 'incoming',
            'use_create_lots': True,
            'use_existing_lots': False,
            'default_location_src_id': False,
            'default_location_dest_id': location_in.id,
            'barcode': self.code.replace(" ", "").upper() + "-RECEIPTS_SALE",
            'show_reserved': False,
            'warehouse_id': self.id,
            'sequence_code': sequence.prefix,
            'sequence_id': sequence.id,
            'company_id': self.company_id.id,
            'active': active
        })
        self.write({'receipt_sale_type_id': receipt_sale_type_obj.id})

    def _create_rule_obj(self, name, action, picking_type_id, wh_src_id, wh_dest_id, method, propagate, route_id):
        self.env['stock.rule'].create({
            'name': name,
            'action': action,
            'picking_type_id': picking_type_id,
            'location_src_id': wh_src_id,
            'location_id': wh_dest_id,
            'procure_method': method,
            'group_propagation_option': propagate,  # Whit this options we can ensure that will be generate only one PO
            'propagate_cancel': True,
            'warehouse_id': False,
            'company_id': self.company_id.id,
            'route_id': route_id
        })

    def _create_buy_rule(self, warehouse, route):
        """
        This function create specific buy's rule
        :params warehouse: Object
        :params route: Object
        """
        in_picking_type_obj = warehouse.in_type_id
        in_picking_type_obj.write({'active': True})
        int_picking_type_obj = warehouse.int_type_id
        int_picking_type_obj.write({'active': True})
        # Check number of reception steps
        if warehouse.reception_steps == 'one_step':
            # [*-> wh/giacenza]
            name = _('Buy for Sold')
            propagate = 'none'
            self._create_rule_obj(name, 'buy', in_picking_type_obj.id, False, warehouse.lot_stock_id.id, 'make_to_stock', propagate, route.id)
        elif warehouse.reception_steps == 'two_steps':
            # [* -> wh/input]
            name = _('Buy for Sold')
            propagate = 'none'
            self._create_rule_obj(name, 'buy', in_picking_type_obj.id, False, warehouse.wh_input_stock_loc_id.id, 'make_to_stock', propagate, route.id)
            # [wh/input -> wh/giacenza]
            name = '%s: %s -> %s (%s)' % (warehouse.code, warehouse.wh_input_stock_loc_id.display_name, warehouse.lot_stock_id.display_name, 'pull')
            propagate = 'propagate'
            self._create_rule_obj(name, 'pull', int_picking_type_obj.id, warehouse.wh_input_stock_loc_id.id, warehouse.lot_stock_id.id, 'make_to_order', propagate, route.id)
        elif warehouse.reception_steps == 'three_steps':
            # [* -> wh/input]
            name = _('Buy for Sold')
            propagate = 'none'
            self._create_rule_obj(name, 'buy', in_picking_type_obj.id, False, warehouse.wh_input_stock_loc_id.id, 'make_to_stock', propagate, route.id)
            # [wh/input -> wh/qualità]
            name = '%s: %s -> %s (%s)' % (warehouse.code, warehouse.wh_input_stock_loc_id.display_name, warehouse.wh_qc_stock_loc_id.display_name, 'pull')
            propagate = 'propagate'
            self._create_rule_obj(name, 'pull', int_picking_type_obj.id, warehouse.wh_input_stock_loc_id.id, warehouse.wh_qc_stock_loc_id.id, 'make_to_order', propagate, route.id)
            # [wh/qualità -> wh/giacenza]
            name = '%s: %s -> %s (%s)' % (warehouse.code, warehouse.wh_qc_stock_loc_id.display_name, warehouse.lot_stock_id.display_name, 'pull')
            self._create_rule_obj(name, 'pull', int_picking_type_obj.id, warehouse.wh_qc_stock_loc_id.id, warehouse.lot_stock_id.id, 'make_to_order', propagate, route.id)

    def _create_shipment_rule(self, wh_source, wh_dest, warehouse_type, route):
        """
        This function create specific shipment's rule
        :params wh_source: Object
        :params wh_dest: Object
        :params warehouse_type: String
        :params route: Object
        """
        if warehouse_type == 'behalf':
            action = 'pull_push'
            shipment_picking_type_obj = wh_source.out_type_id
            shipment_picking_type_obj.write({'active': True})
            procure_method = 'make_to_stock'
        else:
            action = 'pull'
            shipment_picking_type_obj = wh_source.shipment_sale_type_id
            shipment_picking_type_obj.write({'active': True})
            procure_method = 'make_to_order'
        int_picking_type_obj = wh_source.int_type_id
        int_picking_type_obj.write({'active': True})
        propagate = 'propagate'
        # Check number of delivery steps
        if wh_source.delivery_steps == 'ship_only':
            # [wh_source/giacenza -> wh_dest/transito]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.lot_stock_id.display_name, wh_dest.wh_transit_stock_loc_id.display_name, 'pull')
            if warehouse_type == 'pickup':
                self._create_rule_obj(name, action, shipment_picking_type_obj.id, wh_source.lot_stock_id.id, wh_dest.wh_transit_stock_loc_id.id, 'make_to_stock', propagate, route.id)
            else:
                self._create_rule_obj(name, action, shipment_picking_type_obj.id, wh_source.lot_stock_id.id, wh_dest.wh_transit_stock_loc_id.id, procure_method, propagate, route.id)
        elif wh_source.delivery_steps == 'pick_ship':
            # [wh_source/giacenza -> wh_source/uscita]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.lot_stock_id.display_name, wh_source.wh_output_stock_loc_id.display_name, 'pull')
            if warehouse_type == 'pickup':
                self._create_rule_obj(name, action, int_picking_type_obj.id, wh_source.lot_stock_id.id, wh_source.wh_output_stock_loc_id.id, 'make_to_stock', propagate, route.id)
            else:
                self._create_rule_obj(name, action, int_picking_type_obj.id, wh_source.lot_stock_id.id, wh_source.wh_output_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/uscita -> wh_dest/transito]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_output_stock_loc_id.display_name, wh_dest.wh_transit_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, action, shipment_picking_type_obj.id, wh_source.wh_output_stock_loc_id.id, wh_dest.wh_transit_stock_loc_id.id, procure_method, propagate, route.id)
        elif wh_source.delivery_steps == 'pick_pack_ship':
            # [wh_source/giacenza -> wh_source/uscita]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.lot_stock_id.display_name, wh_source.wh_output_stock_loc_id.display_name, 'pull')
            if warehouse_type == 'pickup':
                self._create_rule_obj(name, action, int_picking_type_obj.id, wh_source.lot_stock_id.id, wh_source.wh_output_stock_loc_id.id, 'make_to_stock', propagate, route.id)
            else:
                self._create_rule_obj(name, action, int_picking_type_obj.id, wh_source.lot_stock_id.id, wh_source.wh_output_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/uscita -> wh_source/imballaggio]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_output_stock_loc_id.display_name, wh_source.wh_pack_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, action, int_picking_type_obj.id, wh_source.wh_output_stock_loc_id.id, wh_source.wh_pack_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/imballaggio -> wh_dest/transito]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_pack_stock_loc_id.display_name, wh_dest.wh_transit_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, action, shipment_picking_type_obj.id, wh_source.wh_pack_stock_loc_id.id, wh_dest.wh_transit_stock_loc_id.id, procure_method, propagate, route.id)

    def _create_transit_shipment_rule(self, wh_source, wh_dest, procure_method, route):
        """
        This function create specific transit shipment's rule
        :params wh_source: Object
        :params wh_dest: Object
        :params procure_method: String
        :params route: Object
        """
        receipt_picking_type_obj = wh_source.receipt_sale_type_id
        receipt_picking_type_obj.write({'active': True})
        shipment_sale_type_obj = wh_source.shipment_sale_type_id
        shipment_sale_type_obj.write({'active': True})
        propagate = 'propagate'
        # Check number of delivery steps
        if wh_source.delivery_steps == 'ship_only':
            # [wh_source/transito -> wh_dest/transito]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_transit_stock_loc_id.display_name, wh_dest.wh_transit_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, 'pull', shipment_sale_type_obj.id, wh_source.wh_transit_stock_loc_id.id, wh_dest.wh_transit_stock_loc_id.id, procure_method, propagate, route.id)
        elif wh_source.delivery_steps == 'pick_ship' or wh_source.delivery_steps == 'pick_pack_ship':
            # [wh_source/transito -> wh_source/output]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_transit_stock_loc_id.display_name, wh_source.wh_output_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, 'pull', receipt_picking_type_obj.id, wh_source.wh_transit_stock_loc_id.id, wh_source.wh_output_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/output -> wh_dest/transito]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_output_stock_loc_id.display_name, wh_dest.wh_transit_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, 'pull', shipment_sale_type_obj.id, wh_source.wh_output_stock_loc_id.id, wh_dest.wh_transit_stock_loc_id.id, procure_method, propagate, route.id)

    def _create_receipt_rule(self, wh_source, warehouse_type, route):
        """
        This function create specific receipt's rule
        :params wh_source: Object
        :params warehouse_type: String
        :params route: Object
        """
        if warehouse_type == 'behalf':
            action = 'pull_push'
            receipt_picking_type_obj = wh_source.in_type_id
            receipt_picking_type_obj.write({'active': True})
            procure_method = 'make_to_stock'
        else:
            action = 'pull'
            receipt_picking_type_obj = wh_source.receipt_sale_type_id
            receipt_picking_type_obj.write({'active': True})
            procure_method = 'make_to_order'
        int_picking_type_obj = wh_source.int_type_id
        int_picking_type_obj.write({'active': True})
        propagate = 'propagate'
        # Check number of delivery steps
        if wh_source.reception_steps == 'one_step':
            # [wh_source/transito -> wh_source/giacenza]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_transit_stock_loc_id.display_name, wh_source.lot_stock_id.display_name, 'pull')
            self._create_rule_obj(name, action, receipt_picking_type_obj.id, wh_source.wh_transit_stock_loc_id.id, wh_source.lot_stock_id.id, procure_method, propagate, route.id)
        elif wh_source.reception_steps == 'two_steps':
            # [wh_source/transito -> wh_source/ingresso]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_transit_stock_loc_id.display_name, wh_source.wh_input_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, action, receipt_picking_type_obj.id, wh_source.wh_transit_stock_loc_id.id, wh_source.wh_input_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/ingresso -> wh_source/giacenza]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_input_stock_loc_id.display_name, wh_source.lot_stock_id.display_name, 'pull')
            self._create_rule_obj(name, action, int_picking_type_obj.id, wh_source.wh_input_stock_loc_id.id, wh_source.lot_stock_id.id, procure_method, propagate, route.id)
        elif wh_source.reception_steps == 'three_steps':
            # [wh_source/transito -> wh_source/ingresso]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_transit_stock_loc_id.display_name, wh_source.wh_input_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, action, receipt_picking_type_obj.id, wh_source.wh_transit_stock_loc_id.id, wh_source.wh_input_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/ingresso -> wh_source/qualità]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_input_stock_loc_id.display_name, wh_source.wh_qc_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, action, int_picking_type_obj.id, wh_source.wh_input_stock_loc_id.id, wh_source.wh_qc_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/qualità -> wh_source/giacenza]
            name = '%s: %s -> %s (%s)' % (wh_source.code, wh_source.wh_qc_stock_loc_id.display_name, wh_source.lot_stock_id.display_name, 'pull')
            self._create_rule_obj(name, action, int_picking_type_obj.id, wh_source.wh_qc_stock_loc_id.id, wh_source.lot_stock_id.id, procure_method, propagate, route.id)

    def _create_sell_rule(self, route):
        """
        This function create specific sell's rule
        :params route: Object
        """
        out_picking_type_obj = self.out_type_id
        out_picking_type_obj.write({'active': True})
        int_picking_type_obj = self.int_type_id
        int_picking_type_obj.write({'active': True})
        procure_method = 'make_to_order'
        propagate = 'propagate'
        location_dest = self.env.ref('stock.stock_location_customers')
        # Check number of delivery steps
        if self.delivery_steps == 'ship_only':
            # [wh_source/giacenza -> customer]
            name = '%s: %s -> %s (%s)' % (self.code, self.lot_stock_id.display_name, location_dest.display_name, 'pull')
            self._create_rule_obj(name, 'pull', out_picking_type_obj.id, self.lot_stock_id.id, location_dest.id, procure_method, propagate, route.id)
        elif self.delivery_steps == 'pick_ship':
            # [wh_source/giacenza -> wh_source/uscita]
            name = '%s: %s -> %s (%s)' % (self.code, self.lot_stock_id.display_name, self.wh_output_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, 'pull', int_picking_type_obj.id, self.lot_stock_id.id, self.wh_output_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/uscita -> customer]
            name = '%s: %s -> %s (%s)' % (self.code, self.wh_output_stock_loc_id.display_name, location_dest.display_name, 'pull')
            self._create_rule_obj(name, 'pull', out_picking_type_obj.id, self.wh_output_stock_loc_id.id, location_dest.id, procure_method, propagate, route.id)
        elif self.delivery_steps == 'pick_pack_ship':
            # [wh_source/giacenza -> wh_source/imballaggio]
            name = '%s: %s -> %s (%s)' % (self.code, self.lot_stock_id.display_name, self.wh_output_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, 'pull', int_picking_type_obj.id, self.lot_stock_id.id, self.wh_pack_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/imballaggio -> wh_source/uscita]
            name = '%s: %s -> %s (%s)' % (self.code, self.wh_output_stock_loc_id.display_name, self.wh_pack_stock_loc_id.display_name, 'pull')
            self._create_rule_obj(name, 'pull', int_picking_type_obj.id, self.wh_pack_stock_loc_id.id, self.wh_output_stock_loc_id.id, procure_method, propagate, route.id)
            # [wh_source/uscita -> customer]
            name = '%s: %s -> %s (%s)' % (self.code, self.wh_pack_stock_loc_id.display_name, location_dest.display_name, 'pull')
            self._create_rule_obj(name, 'pull', out_picking_type_obj.id, self.wh_output_stock_loc_id.id, location_dest.id, procure_method, propagate, route.id)

    def _active_pickings_type(self):
        shipment_sale_type_obj = self.shipment_sale_type_id
        if shipment_sale_type_obj and not shipment_sale_type_obj.active:
            _logger.info(_("Restore : ") + shipment_sale_type_obj.name)
            shipment_sale_type_obj.write({'active': True})
        receipt_sale_type_obj = self.receipt_sale_type_id
        if receipt_sale_type_obj and not receipt_sale_type_obj.active:
            _logger.info(_("Restore : ") + receipt_sale_type_obj.name)
            receipt_sale_type_obj.write({'active': True})

    def _create_route(self, warehouses_path, warehouse_type):
        """
        This function allows:
        * to create an appropriate route if it doesn't exist (Note! If route is disabled, makes it active)
        * to create relative picking's type
        * to create relative rule's associated by route
        :params warehouses_path: List
        :params warehouse_type: String (pick-up for pickup warehouses /buy for sale_buy_warehouses)
        """
        route_external_id = "stock_location_route_" + warehouse_type + "_" + "_".join([str(x.id) for x in warehouses_path])
        route_obj = self.env.ref('sale_advanced_mto.' + route_external_id, False)
        if route_obj:
            if not route_obj.active:
                # Active Route, rules and picking types
                _logger.info(_("Restore Route: ") + route_obj.name)
                route_obj.write({'active': True})
                route_obj.with_context(active_test=False).rule_ids.write({'active': True})
                route_obj.rule_ids.with_context(active_test=False).mapped('picking_type_id').write({'active': True})
            return route_obj
        name = self.name + ': ' + ' → '.join([x.code for x in warehouses_path])
        is_default_route = False
        sale_selectable = False
        warehouse_selectable = False
        if warehouse_type == 'behalf':
            name += ' (' + _('Behalf for') + ')'
            warehouse_selectable = True
        elif warehouse_type == 'buy':
            name += ' (' + _('Buy for Sold') + ')'
            sale_selectable = True
            is_default_route = True
        elif warehouse_type == 'pickup':
            name += ' (' + _('Pickup for Sold') + ')'
            sale_selectable = True
            # if the len of the warehouse path is len two it means that is the shorter happy path and may be settings
            # as default route
            is_default_route = len(warehouses_path) == 2

        route_obj = self.env['stock.location.route'].create({
            'name': name,
            'active': True,
            'product_selectable': False,
            'product_categ_selectable': False,
            'warehouse_selectable': warehouse_selectable,
            'sale_selectable': sale_selectable,
            'is_default_route': is_default_route,
            'sequence': 9999  # have to assign high value for the sequence order not to compromise the standard behave.
        })
        # Add external id for this route
        self.env['ir.model.data'].create({
            'module': 'sale_advanced_mto',
            'name': route_external_id,
            'model': 'stock.location.route',
            'res_id': route_obj.id,
            'noupdate': True
        })
        _logger.info(_("Create Route: ") + route_obj.name.__str__())
        # Management Picking type and Rules
        if warehouse_type == 'buy':
            self._create_buy_rule(warehouses_path[0], route_obj)
            if warehouses_path[0] == self:  # Controllo se è il magazzino di destinazione è se stesso
                self._create_sell_rule(route_obj)
                return route_obj
        # Create picking type and rules
        for i, warehouse in enumerate(warehouses_path):
            # Check if shipment_sale_type and receipt_sale_type are active for wh source
            warehouse._active_pickings_type()
            if i == 0 and i != len(warehouses_path) - 1:  # Magazzino iniziale
                self._create_shipment_rule(warehouse, warehouses_path[i + 1], warehouse_type, route_obj)
            elif i != 0 and i != len(warehouses_path) - 1:  # Magazzino di Transito
                self._create_transit_shipment_rule(warehouse, warehouses_path[i+1], 'make_to_order', route_obj)
            elif i == len(warehouses_path) - 1:  # Magazzino finale
                self._create_receipt_rule(warehouse, warehouse_type, route_obj)
        if warehouse_type != 'behalf':
            self._create_sell_rule(route_obj)
        return route_obj

    def _delete_route(self, warehouse_path, warehouse_type):
        """
        This function allows to delete picking type and rules for relative route
        :params warehouse_path: List
        :params warehouse_type: String (buy / pickup)
        """
        route_external_id = "stock_location_route_" + warehouse_type + "_" + "_".join([str(x.id) for x in warehouse_path])
        remove_route_obj = self.env.ref('sale_advanced_mto.' + route_external_id, False)
        if remove_route_obj:
            self.env.cr.execute('SAVEPOINT routeDelete')
            _logger.info(_("Delete Route: ") + remove_route_obj.name)
            try:
                remove_route_obj.unlink()
            except IntegrityError:
                self.env.cr.execute('ROLLBACK TO SAVEPOINT routeDelete')
                remove_route_obj.active = False
                remove_route_obj.rule_ids.write({'active': False})
            self.env.cr.commit()

    def _create_warehouses_path(self, sale_pickup_warehouse_row):
        """
        This function creates a list of warehouse's path (for sale_pickup_warehouse_row passed)
        * Example for one row: [(pickup warehouse, self), (temp_wh1, temp_wh2, temp_whn...)]
        :params sale_pickup_warehouse_row: Dictionary with key picking_type_id and temporary_warehouses_ids
        """
        # Self is warehouse that is being created/updated
        result = []
        pickup_warehouse_id = sale_pickup_warehouse_row['pickup_warehouse_id']
        pickup_warehouse_obj = self.env['stock.warehouse'].browse(pickup_warehouse_id)
        result.append([pickup_warehouse_obj, self])
        temporary_warehouse_ids = sale_pickup_warehouse_row['temporary_warehouse_ids']
        if temporary_warehouse_ids:
            temporary_warehouses_list = [pickup_warehouse_obj]
            for temporary_warehouse_id in temporary_warehouse_ids:
                temporary_warehouse_obj = self.env['stock.warehouse'].browse(temporary_warehouse_id)
                temporary_warehouses_list.append(temporary_warehouse_obj)
            temporary_warehouses_list.append(self)
            result.append(temporary_warehouses_list)
        return result

    def _manage_buy_and_pickup_warehouses(self, type_warehouses, warehouse_dict):
        """
        This function allows:
        * remove relative Routes (with picking type, rules)
        * create relative Routes
        :params type_warehouses: behalf /buy / pickup warehouses
        :params warehouse_dict: Dictionary (sale_buy_dict/pickup_dict)
        """
        # Warehouses to remove: build remove warehouses paths
        remove_warehouse_paths = []
        add_warehouse_paths = []
        # SaleBuyBehalf warehouses
        if type_warehouses == 'behalf':
            if 'remove' in warehouse_dict:
                remove_behalf_warehouses = warehouse_dict['remove']
                for remove_behalf_warehouse_obj in remove_behalf_warehouses:
                    delete_row_behalf_path = [self, remove_behalf_warehouse_obj]
                    remove_warehouse_paths.extend([delete_row_behalf_path])
            if 'add' in warehouse_dict:
                add_behalf_warehouses = warehouse_dict['add']
                for add_behalf_warehouse_obj in add_behalf_warehouses:
                    add_row_behalf_path = [self, add_behalf_warehouse_obj]
                    add_warehouse_paths.extend([add_row_behalf_path])
        # SaleBuy warehouses
        elif type_warehouses == 'buy':
            if 'remove' in warehouse_dict:
                remove_warehouses = warehouse_dict['remove']
                for remove_warehouse_obj in remove_warehouses:
                    delete_row_path = [remove_warehouse_obj, self]
                    remove_warehouse_paths.extend([delete_row_path])
            if 'add' in warehouse_dict:
                # Warehouses to Add: build add warehouses paths (Example: [[wh1, wh2],[wh1,wh3,wh4]]
                add_warehouses = warehouse_dict['add']
                for add_warehouse_obj in add_warehouses:
                    add_row_path = [add_warehouse_obj, self]
                    add_warehouse_paths.extend([add_row_path])
        # Pickup warehouses
        elif type_warehouses == 'pickup':
            if 'remove' in warehouse_dict:
                remove_pickup_warehouses = warehouse_dict.get('remove')
                for remove_warehouse_path in remove_pickup_warehouses:
                    dict_pickup_row = {
                        'pickup_warehouse_id': remove_warehouse_path[0],
                        'temporary_warehouse_ids': remove_warehouse_path[1:]
                    }
                    row_paths = self._create_warehouses_path(dict_pickup_row)
                    remove_warehouse_paths.extend(row_paths)
            if 'add' in warehouse_dict:
                add_pickup_warehouses = warehouse_dict.get('add')
                for add_warehouse_path in add_pickup_warehouses:
                    dict_pickup_row = {
                        'pickup_warehouse_id': add_warehouse_path[0],
                        'temporary_warehouse_ids': add_warehouse_path[1:]
                    }
                    row_paths = self._create_warehouses_path(dict_pickup_row)
                    add_warehouse_paths.extend(row_paths)

        # Remove Route for each remove_path: (Example: [[wh1, wh2],[wh1,wh3,wh4]]
        for path in remove_warehouse_paths:
            self._delete_route(path, type_warehouses)
        # Example of path: [Wh_source -> Wh_dest] (in this case wh_dest is warehouse that's being created or updated)
        for path in add_warehouse_paths:
            new_route_obj = self._create_route(path, type_warehouses)
            # Associated route in self warehouse
            self.write({'route_ids': [(4, new_route_obj.id, 0)]})
            if type_warehouses == 'behalf':
                new_route_obj.warehouse_ids = None

    def _retrieve_pickup_warehouses(self):
        """
        This function returns a order warehouse's path list
        """
        sale_pickup_list = []
        for sale_pickup_row in self.sale_pick_up_from_ids:
            ordered_pickup_warehouse_rel_obj = self.env['sale.pickup.warehouse.rel'].search([(
                'warehouse_sale_pickup_id', '=', sale_pickup_row.id
            )], order="sequence, id")
            temporary_warehouse_ids = []
            for pickup_warehouse_rel in ordered_pickup_warehouse_rel_obj:
                temporary_warehouse_ids.append(pickup_warehouse_rel.warehouse_id.id)
            if temporary_warehouse_ids:
                sale_pickup_list.extend([temporary_warehouse_ids])
        return sale_pickup_list

    def _get_transit_locations(self):
        internal_transit_location, external_transit_location = self.wh_transit_stock_loc_id, self.wh_transit_stock_loc_id
        return internal_transit_location, external_transit_location

    @api.model
    def create(self, vals):
        warehouse = super(StockWarehouse, self).create(vals)
        # Acquisto per conto di
        if vals.get('sale_buy_behalf_ids'):
            buy_behalf = {'add': warehouse.sale_buy_behalf_ids}
            warehouse._manage_buy_and_pickup_warehouses('behalf', buy_behalf)
        # Compra ricevendo in
        if vals.get('sale_buy_receving_in_ids'):
            buy_dict = {'add': warehouse.sale_buy_receving_in_ids}
            warehouse._manage_buy_and_pickup_warehouses('buy', buy_dict)
        # Prendi da
        if vals.get('sale_pick_up_from_ids'):
            new_sale_pickup_dict = warehouse._retrieve_pickup_warehouses()
            pickup_dict = {'add': new_sale_pickup_dict}
            warehouse._manage_buy_and_pickup_warehouses('pickup', pickup_dict)
        return warehouse

    def write(self, vals):
        res = True
        # Check old and new sale buy/pickup warehouses
        for record in self:
            # Sale buy behalf warehouses
            if vals.get('sale_buy_behalf_ids'):
                sale_buy_behalf_warehouses_whs = record.resolve_2many_commands(
                    'sale_buy_behalf_ids', vals['sale_buy_behalf_ids']
                )
                new_sale_buy_behalf_warehouses = record.browse([wh['id'] for wh in sale_buy_behalf_warehouses_whs])
                old_sale_buy_behalf_warehouses = {warehouse.id: warehouse.sale_buy_behalf_ids for warehouse in record}
            # Sale buy warehouses
            if vals.get('sale_buy_receving_in_ids'):
                sale_buy_warehouses_whs = record.resolve_2many_commands(
                    'sale_buy_receving_in_ids', vals['sale_buy_receving_in_ids']
                )
                new_sale_buy_warehouses = record.browse([wh['id'] for wh in sale_buy_warehouses_whs])
                old_sale_buy_warehouses = {warehouse.id: warehouse.sale_buy_receving_in_ids for warehouse in record}
            # Pickup warehouses
            if vals.get('sale_pick_up_from_ids'):
                old_sale_pickup_dict = record._retrieve_pickup_warehouses()
            res |= super(StockWarehouse, record).write(vals)
        for record in self:
            if 'reception_steps' in vals or 'delivery_steps' in vals:
                self._update_receipt_ship_sale_picking_type()
            # Sale buy behalf warehouses
            if vals.get('sale_buy_behalf_ids'):
                add_sale_buy_behalf_warehouses = new_sale_buy_behalf_warehouses - old_sale_buy_behalf_warehouses[record.id]
                remove_sale_buy_behalf_warehouses = old_sale_buy_behalf_warehouses[record.id] - new_sale_buy_behalf_warehouses
                sale_buy_behalf_dict = {
                    'remove': remove_sale_buy_behalf_warehouses,
                    'add': add_sale_buy_behalf_warehouses
                }
                record._manage_buy_and_pickup_warehouses('behalf', sale_buy_behalf_dict)
            # Sale buy warehouses
            if vals.get('sale_buy_receving_in_ids'):
                add_sale_buy_warehouses = new_sale_buy_warehouses - old_sale_buy_warehouses[record.id]
                remove_sale_buy_warehouses = old_sale_buy_warehouses[record.id] - new_sale_buy_warehouses
                sale_buy_dict = {
                    'remove': remove_sale_buy_warehouses,
                    'add': add_sale_buy_warehouses
                }
                record._manage_buy_and_pickup_warehouses('buy', sale_buy_dict)
            # Sale pickup warehouses
            if vals.get('sale_pick_up_from_ids'):
                new_sale_pickup_dict = record._retrieve_pickup_warehouses()
                pickup_dict = {
                    'remove': old_sale_pickup_dict,
                    'add': new_sale_pickup_dict
                }
                record._manage_buy_and_pickup_warehouses('pickup', pickup_dict)
        return res

    @api.constrains('sale_pick_up_from_ids')
    def _check_sale_pickup(self):
        for record in self:
            for sale_pickup in record.sale_pick_up_from_ids:
                if not sale_pickup.temporary_warehouse_ids:
                    raise ValidationError(
                        _("Can't enter empty paths, please remove it!")
                    )

    @api.constrains('reception_steps', 'delivery_steps')
    def _check_warehouse_steps(self):
        for record in self:
            if record._is_active_receipt_ship_sale_picking_type():
                raise ValidationError(_("Unable to change steps for this warehouse cause of exists specific routes."
                                        "Please delete this routes to proceed."))

    def _update_transit_location(self):
        """
        This function is called when module is installed: allows to update wh_transition_location
        """
        transit_location_warehouse = self.env['stock.location'].with_context(active_test=False).search([
            ('location_id', '=', self.view_location_id.id),
            ('usage', '=', 'transit')
        ])
        if not self.wh_transit_stock_loc_id:
            if not transit_location_warehouse:
                vals = {
                    'name': _('Transit'),
                    'active': True,
                    'usage': 'transit',
                    'barcode': self._valid_barcode(self.code + '-TRANSIT', self.company_id.id),
                    'company_id': self.company_id.id,
                    'location_id': self.view_location_id.id
                }
                new_transit_location = self.env['stock.location'].create(vals)
                self.write({'wh_transit_stock_loc_id': new_transit_location.id})
            else:
                self.write({'wh_transit_stock_loc_id': transit_location_warehouse.id})
            _logger.info(_('Associated Transit location to warehouse: ') + self.name)

    def _is_active_receipt_ship_sale_picking_type(self):
        if any([self.sale_buy_receving_in_ids, self.sale_pick_up_from_ids]):
            return True
        all_routes_external_id = self.env['ir.model.data'].search([
            ('model', '=', 'stock.location.route'),
            ('module', '=', 'sale_advanced_mto')
        ])
        if all_routes_external_id:
            all_routes_id = all_routes_external_id.mapped('res_id')
            all_routes_by_external_id = self.env['stock.location.route'].browse(all_routes_id)
            list_warehouses = all_routes_by_external_id.mapped('rule_ids.picking_type_id.warehouse_id').ids
            if list_warehouses and self.id in list_warehouses:
                return True
        return False

    def _update_receipt_ship_sale_picking_type(self):
        input_loc, output_loc = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        self.receipt_sale_type_id.default_location_dest_id = input_loc.id
        self.shipment_sale_type_id.default_location_src_id = output_loc.id

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get('only_wh_dest', False):
            picking_type_obj = self.env['stock.picking.type'].browse(self._context.get('picking_type_id', False))
            origin_warehouse_obj = picking_type_obj.warehouse_id if picking_type_obj else False
            warehouses_ids = []
            if origin_warehouse_obj:
                warehouses_ids = origin_warehouse_obj.sale_buy_behalf_ids.ids
            domain = expression.AND([args or [], [('id', 'in', warehouses_ids)]])
            return super(StockWarehouse, self.sudo())._name_search(name=name, args=domain, operator=operator, limit=limit, name_get_uid=SUPERUSER_ID)
        return super(StockWarehouse, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
