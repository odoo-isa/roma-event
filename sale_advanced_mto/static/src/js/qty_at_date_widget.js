odoo.define('sale_advanced_mto.QtyAtDateWidget', function (require) {
"use strict";

    var core = require('web.core');
    var config = require('web.config');
    var time = require('web.time');
    var data_manager = require('web.data_manager');
    var Context = require('web.Context');
    var Dialog = require('web.Dialog');
    var qtyAtDateWidget = require('sale_stock.QtyAtDateWidget');
    const RelationalFields = require('web.relational_fields');
    const BasicFields = require('web.basic_fields');
    var field_utils = require('web.field_utils');
    var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
    var utils = require('web.utils');
    const session = require('web.session');

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var QWeb = core.qweb;
    var _t = core._t;
    var round_pr = utils.round_precision;

    var QtyAtDateWidget = qtyAtDateWidget.include({
        /*
         * Override to mange multiple button action
         * on content popover
         */
        _setPopOver: function(){
            var self = this;
            if (!this.data.scheduled_date) {
                return;
            }
            this.data.delivery_date = this.data.scheduled_date.clone().add(this.getSession().getTZOffset(this.data.scheduled_date), 'minutes').format(time.getLangDateFormat());
            // The grid view need a specific date format that could be different than
            // the user one.
            this.data.delivery_date_grid = this.data.scheduled_date.clone().add(this.getSession().getTZOffset(this.data.scheduled_date), 'minutes').format('YYYY-MM-DD');
            this.data.debug = config.isDebug();
            var $content = $(QWeb.render('sale_stock.QtyDetailPopOver', {
                data: this.data,
            }));
            this._bindEventOnButton($content);
            var options = {
                content: $content,
                html: true,
                placement: 'left',
                title: _t('Availability'),
                trigger: 'focus',
                delay: {'show': 0, 'hide': 100 },
            };
            this.$el.popover(options);
        },
        _replenish: function(){
            var self = this;
            var mto_route_dialog = new SaleMtoRoute(this,{
                title: _t('Replenish Product'),
                buttons: [
                    {
                        text: _t('Ok'),
                        classes: 'btn-primary',
                        click: function () {
                            try{
                                this._perform_check();
                            }catch(err){
                                self.do_warn(_t("Error"), err.message);
                                return;
                            }
                            let happy_path = this.value;
                            self._rpc({
                                model: 'sale.order.line',
                                method: 'dispatch_lines_by_routing',
                                args: [self.data.id],
                                kwargs: {
                                    'happy_path': happy_path
                                }
                            }).then(function(){
                                self.trigger_up('reload');
                            });
                        }
                    }
                ]
            })
            mto_route_dialog.open();
        },
        _bindEventOnButton: function($content){
            var self = this;
            //Forecast button
            var $forecastButton = $content.find('.action_open_forecast');
            $forecastButton.on('click', function(ev) {
                ev.stopPropagation();
                data_manager.load_action('stock.report_stock_quantity_action_product').then(function (action) {
                    // Change action context to choose a specific date and product(s)
                    // As grid_anchor is set to now() by default in the data, we need
                    // to load the action first, change the context then launch it via do_action
                    // additional_context cannot replace a context value, only add new
                    //
                    // in case of kit product, the forecast view show the kit's components
                    self._rpc({
                        model: 'product.product',
                        method: 'get_components',
                        args: [[self.data.product_id.data.id]]
                    }).then(function (res) {
                        var additional_context = {};
                        additional_context.grid_anchor = self.data.delivery_date_grid;
                        additional_context.search_default_warehouse_id = [self.data.warehouse_id.data.id];
                        action.context = new Context(action.context, additional_context);
                        action.domain = [
                            ['product_id', 'in', res]
                        ];
                        self.do_action(action);
                    });
                });
            });
            //Replenish button
            var $replenishButton = $content.find('.action_open_replenish');
            $replenishButton.on('click', function(ev){
                ev.stopPropagation();
                self._replenish.apply(self);
            });
        }
    });

    /* Dialog Widget */
    var SaleMtoRoute = Dialog.extend(StandaloneFieldManagerMixin, {
        template: 'sale_advanced_mto.RoutingHeader',
        events: _.extend({}, Dialog.prototype.events, {
            'change input.o_field_float': 'field_value_change',
            'click .revert_to_default': 'revert_to_default_warehouse'
        }),
        custom_events: _.extend({}, Dialog.prototype.custom_events, StandaloneFieldManagerMixin.custom_events, {
            'value_changed': 'field_value_change'
        }),
        init: function(parent){
            this._super.apply(this, arguments);
            StandaloneFieldManagerMixin.init.call(this);
            this.alternative_routing = null;
            this.has_routing_buy = null;
            this.formatFloat = field_utils.format.float;
            this.digits = {};
            //Widget Registries
            this.widget_fields = {};
            //Widget values
            this.value = {};
            this.has_group_uom = false;
            this.has_group_salesman_all_leads = false;
        },
        willStart: function(){
            var self = this;
            return Promise.all([
                this._retrieve_alternative_routing(),
                this._get_precision(),
                this._super.apply(this, arguments),
                session.user_has_group('uom.group_uom').then(function(data){
                    self.has_group_uom = data;
                }),
                session.user_has_group('sales_team.group_sale_salesman_all_leads').then(function(data){
                    self.has_group_salesman_all_leads = data;
                })
            ])
        },
        start: function(){
            var self = this,
                defs = [
                    this._super.apply(this, arguments),
                    this.field_value_change()
                ];
            //Prepare routing and float fields
            _.each(this.alternative_routing, function(item, index){
                self._adding_field_to_view(item, index, defs);
            });
            return Promise.all(defs);
        },
        _adding_field_to_view: function(item, index, defs){
            var self = this;
            // Prepare the routing field
            var route = {
                label: 'Route',
                type: 'many2one',
                modelName: 'stock.location.route',
            };
            // PULL
            if(!_.isEmpty(item.routing_pull)){
                var c_route = Object.assign({}, route);
                c_route['domain'] = [['id', 'in', item.routing_pull]];
                defs.push(
                    self._makeM2OField(c_route, "Route").then(function(res){
                        self.widget_fields[`route_pull_${index}`] = res;
                        res.appendTo(self.$el.find(`td.route_pull_${index}`));
                    })
                )
            }
            // BUY
            if(!_.isEmpty(item.routing_buy)){
                var c_route = Object.assign({}, route);
                c_route['domain'] = [['id', 'in', item.routing_buy]];
                defs.push(
                    self._makeM2OField(c_route, "Route").then(function(res){
                        self.widget_fields[`route_buy_${index}`] = res;
                        res.appendTo(self.$el.find(`td.route_buy_${index}`));
                    })
                )
            }
        },
        _retrieve_alternative_routing: function(){
            var self = this,
                warehouse_id = null,
                product_id = this.getParent().data.product_id.data.id,
                delivery_date = null,
                sale_order_line = this.getParent().data.id,
                d = new $.Deferred();
            if(this.getParent().data.force_data && 'warehouse_id' in this.getParent().data.force_data){
                warehouse_id = this.getParent().data.force_data.warehouse_id;
            }else{
                warehouse_id = this.getParent().data.warehouse_id.data.id;
            }
            if(this.getParent().data.force_data && 'delivery_date' in this.getParent().data.force_data){
                delivery_date = this.getParent().data.force_data.delivery_date;
            }else{
                delivery_date = this.getParent().data.scheduled_date.toJSON();
            }
            this._rpc({
                model: 'qty.at.date',
                method: 'retrieve_alternative_routing',
                args: [sale_order_line, warehouse_id, product_id, delivery_date]
            }).then(function(data){
                self.alternative_routing = data;
                // Value if present buy routing and pull routing. It will be used in the template
                // buy
                let routing_buy = _.pluck(self.alternative_routing, 'routing_buy');
                routing_buy = _.filter(routing_buy, (r)=>{ return r;});
                self.has_routing_buy = !_.isEmpty(routing_buy);
                d.resolve();
            });
            return d.promise();
        },
        _get_precision: function(){
            var self = this,
                d = new $.Deferred();
            this._rpc({
                model: 'qty.at.date',
                method: 'get_precision',
                args: [self.getParent().data.product_uom.data.id]
            }).then(function(data){
                self.digits = data;
                d.resolve();
            });
            return d.promise();
        },
        _makeM2OField: function(fieldInfo, fieldName){
            var self = this,
                options = {},
                d = new $.Deferred(),
                options = {};
            options[fieldName] = {
                options: {
                    no_create_edit: true,
                    no_create: true,
                    no_open: true
                }
            };
            this.model.makeRecord(fieldInfo.modelName, [{
                name: fieldName,
                relation: fieldInfo.modelName,
                domain: fieldInfo.domain || [],
                type: fieldInfo.type,
            }], options).then(function (recordID) {
                let attrs = {}
                if(self.has_group_salesman_all_leads){
                    attrs['mode'] = 'edit';
                }else{
                    attrs['readonly'] = 'true';
                    attrs['force_save'] = 'true';
                }
                var m2o_widget = new RelationalFields.FieldMany2One(self,
                    fieldName,
                    self.model.get(recordID),
                    attrs
                );
                self._registerWidget(recordID, fieldName, m2o_widget);
                d.resolve(m2o_widget);
            });
            return d.promise();
        },
        _confirmChange: function(){
            var self = this;
            var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
            this.trigger_up('value_changed');
            return result;
        },
        field_value_change: function(ev){
            // From event retrieve which field had changed to get the default route if exists
            if(ev){
                this._set_default_route(ev);
            }
            this.value = this.serialize_data();
            this._update_qty_procured();
        },
        _set_default_route: function(ev){
            let input_field = ev.target;
            let warehouse_data = $(input_field).closest('tr').data('warehouse');
            if(!warehouse_data) return;
            warehouse_data = warehouse_data.split("_");
            // Retrieve the type from warehouse data attribute
            let type = warehouse_data[0];
            let warehouse = warehouse_data[1];
            // Retrieve the default routing (if exists)
            let default_route = this.alternative_routing[warehouse][`routing_${type}_default`];
            //If no default route, return
            if(!default_route) return;
            // set the default route
            let route = this.widget_fields[`route_${type}_${warehouse}`];
            if(!route) return;
            //Retrieve the value of the field
            let qty = $(input_field).val();
            if (qty == 0){
                route._setValue("");
                return;
            }
            if(route.value.res_id) return;
            route._setValue(default_route);
        },
        _update_qty_procured: function(){
            let qty_procured = this._get_qty_procured();
            let qty_to_replenish = this.getParent().data.product_uom_qty;
            let qty_available_today = this.getParent().data.qty_available_today;
            let qty_from_default = qty_to_replenish - qty_procured;
            if(qty_available_today < 0 ) qty_available_today = 0;
            if(qty_from_default < 0 ) qty_from_default = 0;
            else if (qty_from_default > qty_available_today) qty_from_default = qty_available_today;
            let qty_procured_string = this.formatFloat(qty_procured + qty_from_default);
            // Update the field
            this.$el.find('span#qty_from_default').text(this.formatFloat(qty_from_default));
            let span_class = ''
            if(qty_procured + qty_from_default < qty_to_replenish){
                span_class = 'text-warning';
            }else if(qty_procured + qty_from_default == qty_to_replenish){
                span_class = 'text-success';
            }else{
                span_class = 'text-danger';
            }
            let $qty_procured = this.$el.find('span#qty_procured');
            $qty_procured.removeClass();
            $qty_procured.addClass(span_class);
            $qty_procured.text(qty_procured_string);
            $qty_procured.data('value', qty_procured);
        },
        _get_qty_procured: function(){
            let qty_procured = 0;
            _.each(this.value.pull_rule, function(item){
                qty_procured += item[0];
            });
            _.each(this.value.buy_rule, function(item){
                qty_procured += item[0];
            });
            return qty_procured;
        },
        serialize_data: function(){
            var self = this;
            var result = {
                'pull_rule': {},
                'buy_rule': {}
            };
            // Search for the pull quantity
            var $pull_row = this.$el.find('tr[data-warehouse^="pull"]');
            result['pull_rule'] = this._get_table_data($pull_row);
            // Search for the buy quantity
            var $buy_row = this.$el.find('tr[data-warehouse^="buy"]');
            result['buy_rule'] = this._get_table_data($buy_row);
            // Return the result
            return result;
        },
        _get_table_data: function(row){
            var self = this,
                result = {};
            _.each(row, function(item, $index){
                // Calling check - If error continue
                if(self._rowHasError(item)['error']) return;
                // Retrieve the type
                let info = $(item).data('warehouse').split("_");
                let type = info[0];
                // Retrieve the warehouse
                let warehouse = info[1];
                // Retrieve and float the qty
                let qty = $(item).find(`input[name^=qty_${type}]`).val();
                if(qty<=0) return;
                qty = parseFloat(qty);
                qty = round_pr(qty, self.digits.rounding);
                // Retrieve route

                let route = self.widget_fields[`route_${type}_${warehouse}`];
                result[warehouse] = [qty, route.value.res_id];
            });
            return result;
        },
        _rowHasError: function(row){
            /*
             * Check for the row.
             * return dictionary with error and error message
             */
            var self = this;
            let res = {
                'error': false,
                'error_message': ''
            }
            try{
                let qty = $(row).find('input[name^=qty_]').val();
                qty = parseFloat(qty);
                qty = round_pr(qty, this.digits.rounding);
                //Quantity must be greater or equal than zero
                if(qty<0)
                    throw {
                        name: "ReplenishError",
                        message: _t("Quantity must be greater or equal than zero.")
                    }
                let info = $(row).data('warehouse').split("_");
                let type = info[0];
                let warehouse = info[1];
                //Only pull rule
                let origin_qty = $(row).find('span[data-value]').data('value');
                if(type == 'pull' && origin_qty < qty)
                    throw {
                        name: "ReplenishError",
                        message: _t("Quantity to Pull must be less or equal to the available quantity.")
                    }
                let route = self.widget_fields[`route_${type}_${warehouse}`];
                if((qty>0 && !route.value.res_id) || (qty==0 && route && route.value.res_id))
                    throw {
                        name: "ReplenishError",
                        message: _t("Must be selected the route and the quantity.")
                    }

                $(row).removeClass('table-danger');
            }catch (err){
                if (err.name == 'ReplenishError') {
                    $(row).addClass('table-danger');
                    res.error = true;
                    res.error_message = err.message;
                }else{
                    throw err;
                }
            }
            return res;
        },
        _perform_check: function(){
            var self = this;
            // Check if qty procured is greater than requires qty
            let qty_procured = this._get_qty_procured();
            let qty_required = this.getParent().data.product_uom_qty;
            if(qty_procured > qty_required){
                throw new Error(_t("Procured quantity must be less or equal to the required quantity."));
            }
            // Check the quantity of each pull request line. Must be equal or less than the available quantity.
            var $pull_row = this.$el.find('tr[data-warehouse]');
            _.each($pull_row, function(item){
                let error = self._rowHasError(item);
                if(error.error) throw new Error(error.error_message);
            });
        },
        revert_to_default_warehouse: function(){
            if(!this.getParent().data.route_id) return;
            var self = this;
            self._rpc({
                model: 'sale.order.line',
                method: 'revert_route_to_default_warehouse',
                args: [[self.getParent().data.id]]
            }).then(function (res) {
                self.trigger_up('reload');
            });
        }
    });


    var CancelledRouteWidget = Widget.extend({
        template: 'sale_advanced_mto.cancelledRoute',
        events: _.extend({}, Widget.prototype.events, {
            'click .fa-retweet': '_onClickButton',
        }),
        custom_events: _.extend({}, Widget.prototype.custom_events, {
            'go_replenish': '_go_replenish'
        }),
        /**
         * @override
         * @param {Widget|null} parent
         * @param {Object} params
         */
        init: function (parent, params) {
            this.data = params.data;
            this._super(parent);
            this.qty_at_date = null;
            this.params = params;
            this.force_data = {};
        },
        willStart: function(){
            // If widget is not display doesn't need to call retrieve info function.
            if(!this.data.display_cancelled_route_widget || !this.data.id){
                return this._super.apply(this, arguments);
            }
            var defs = [
                this._super.apply(this, arguments),
                this._retrieveStartData(),
            ];
            return Promise.all(defs);
        },
        _retrieveStartData: async function(){
            var d = new $.Deferred(),
                self = this;
            let order_id = await this._rpc({
                model: 'sale.order.line',
                method: 'read',
                args: [[this.data.id], ['order_id']],
                kwargs: {context: session.user_context}
            });
            order_id = order_id[0].order_id[0];
            let order_data = await this._rpc({
                model: 'sale.order',
                method: 'read',
                args: [[order_id], ['warehouse_id', 'expected_date']],
                kwargs: {context: session.user_context}
            });
            this.force_data.warehouse_id = order_data[0].warehouse_id[0];
            this.force_data.warehouse_name = order_data[0].warehouse_id[1];
            this.force_data.delivery_date = order_data[0].expected_date;
            d.resolve(this.force_data);
            return d.promise();
        },
        _go_replenish: function(){
            //Call replenish function
            this.params.data.force_data = this.force_data;
            this.qty_at_date = new qtyAtDateWidget(this, this.params);
            this.qty_at_date._replenish();
        },
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        _onClickButton: function () {
            // We add the property special click on the widget link.
            // This hack allows us to trigger the click (see _openReplenish) without
            // triggering the _onRowClicked that opens the order line form view.
            this.$el.find('.fa-retweet').prop('special_click', true);
            this.trigger_up('go_replenish');
        }
    });

    widget_registry.add('cancelled_route', CancelledRouteWidget);

    return {
        QtyAtDateWidget: QtyAtDateWidget,
        SaleMtoRoute: SaleMtoRoute,
        CancelledRouteWidget: CancelledRouteWidget
    };

});