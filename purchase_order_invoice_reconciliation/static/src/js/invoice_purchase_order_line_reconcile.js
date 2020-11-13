odoo.define('purchase_order_invoice_reconciliation.reconciliation', function (require) {
'use strict';

var core = require('web.core');
var AbstractAction = require('web.AbstractAction');
var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
var RelationalFields = require('web.relational_fields');
var BasicFields = require('web.basic_fields');
var Widget = require('web.Widget');

var Qweb = core.qweb;
var _t = core._t;

/* Object for the creation of the filters */
var FieldFilters = Widget.extend(StandaloneFieldManagerMixin, {
     /**
      * @constructor
      * @param {Object} fields
      */
    init: function (parent, fields) {
        this._super.apply(this, arguments);
        StandaloneFieldManagerMixin.init.call(this);
        this.fields = fields;
        this.widgets = {};
    },
    /**
     * @override
     */
    willStart: function () {
        var self = this;
        var defs = [this._super.apply(this, arguments)];
        _.each(this.fields, function (field, fieldName) {
            if(field.type == 'many2many') defs.push(self._makeM2MWidget(field, fieldName));
            else if (field.type == 'char') defs.push(self._makeCharWidget(field, fieldName));
        });
        return Promise.all(defs);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        var $content = $(Qweb.render("m2mWidgetTable", {fields: this.fields}));
        self.$el.append($content);
        _.each(this.fields, function (field, fieldName) {
            self.widgets[fieldName].appendTo($content.find('#'+fieldName+'_field'));
        });
        return this._super.apply(this, arguments);
    },
    /**
     * This method will be called whenever a field value has changed and has
     * been confirmed by the model.
     *
     * @private
     * @override
     * @returns {Promise}
     */
    _confirmChange: function () {
        var self = this;
        var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
        var data = {};
        _.each(this.fields, function (filter, fieldName) {
            if(filter.type == 'many2many') data[fieldName] = self.widgets[fieldName].value.res_ids;
            else if(filter.type == 'char') data[fieldName] = self.widgets[fieldName].value;
        });
        this.trigger_up('value_changed', data);
        return result;
    },
    /**
     * This method will create a record and initialize M2M widget.
     *
     * @private
     * @param {Object} fieldInfo
     * @param {string} fieldName
     * @returns {Promise}
     */
    _makeM2MWidget: function (fieldInfo, fieldName) {
        var self = this;
        var options = {};
        options[fieldName] = {
            options: {
                no_create_edit: true,
                no_create: true,
            }
        };
        return this.model.makeRecord(fieldInfo.modelName, [{
            fields: [{
                name: 'id',
                type: 'integer',
            }, {
                name: 'display_name',
                type: 'char',
            }],
            name: fieldName,
            relation: fieldInfo.modelName,
            domain: fieldInfo.domain || [],
            type: fieldInfo.type || 'many2many',
            value: fieldInfo.value,
        }], options).then(function (recordID) {
            self.widgets[fieldName] = new RelationalFields.FieldMany2ManyTags(self,
                fieldName,
                self.model.get(recordID),
                {mode: 'edit',}
            );
            self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
        });
    },
    _makeCharWidget: function(fieldInfo, fieldName){
        var self = this;
        return this.model.makeRecord(fieldName, [{
            name: fieldName,
            type: fieldInfo.type || 'char'
        }]).then(function(recordID){
            self.widgets[fieldName] = new BasicFields.InputField(self,
                fieldName,
                self.model.get(recordID),
                {mode: 'edit'}
            );
            self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
        });
    }
});

var invoiceOrderLineReconcileWidget = AbstractAction.extend({
    template: 'invoice_purchase_order_line_reconciliation',
    events: {
        'click #refresh': 'refresh_data',
        'click input#select-all': 'select_all',
        'change input.line_check': 'set_qty_to_reconcile',
        'click button#reconcile': 'reconcile'
    },
    custom_events: {
        'value_changed': 'load_orders'
    },
    hasControlPanel: true,
    init: function(parent, action) {
        this.invoice_id = action.params.invoice_id;
        this.supplier_id = action.params.supplier_id;
        this.mode = action.params.mode;
        this._super.apply(this, arguments);
        //Invoice View
        this.$invoiceView = null;
        this.FieldFilters = null;
        this.$searchview_buttons = null;
        this.order_ids = []
    },
    willStart: function(){
        var self = this;
        return Promise.all([
            this._super.apply(this, arguments),
            self.load_invoice_view(),
        ]);
    },
    load_invoice_view: function(){
        var self = this;
        var d = new $.Deferred();
        self._rpc({
            model: 'invoice.purchase.order.line.reconcile.widget',
            method: 'get_invoice_view',
            kwargs: {
                invoice_id: self.invoice_id
            }
        }).then(function(view){
            self.$invoiceView = view;
            d.resolve();
        });
        return d.promise();
    },
    start: function(){
        var self = this;
        return Promise.all([
            this.render_filters(),
            this.render_invoice(),
            this.load_order_lines(),
            this._super.apply(this, arguments),
        ]).then(function() {
            self.render();
            //Dynamic event
            $('body').on('click', 'button.unreconciled', self.unreconciled.bind(self));
        });
    },
    render: function(){
        var self = this;
        // Prepare the search box
        this.render_searchview_buttons();
        // Update the control view
        this.update_cp();
    },
    render_searchview_buttons: function(){
        var self = this;
        if(!this.FieldFilters){
            var fields = this.adding_filter_fields();
            if(!_.isEmpty(fields)){
                this.FieldFilters = new FieldFilters(this, fields);
                this.FieldFilters.appendTo(this.$searchview_buttons.find('.js_order_m2m'));
            }
        }
    },
    adding_filter_fields: function(){
        var fields = {},
            self = this;
        fields['order_ids'] = {
            label: _t('Purchase orders'),
            type: 'many2many',
            modelName: 'purchase.filter.reconcile',
            domain: [
                ['supplier_id', '=', self.supplier_id],
            ]
        };
        return fields;
    },
    update_cp: function() {
        var status = {
            cp_content: {
                $searchview_buttons: this.$searchview_buttons,
            },
        };
        return this.updateControlPanel(status, {clear: true});
    },
    render_filters: function(){
        if(this.mode == 'edit') this.$searchview_buttons = $(Qweb.render('filter_fields'));
        else this.$searchview_buttons = $("");
    },
    render_invoice: function(){
        this.$el.find('div#invoice_form').html(this.$invoiceView);
    },
    prepare_info_popover: function(){
        var self = this;
        var popover_content = function($element){
            var d = new $.Deferred();
            var purchase_order_line = $element.closest('tr').data('order-line-id');
            self._rpc({
                model: 'invoice.purchase.order.line.reconcile.widget',
                method: 'get_billed_info',
                args: [purchase_order_line, self.mode]
            }).then(function(result){
                d.resolve(result);
            });
            return d.promise();
        };
        var isRTL = _t.database.parameters.direction === "rtl";
        this.$el.find('i[data-role="billed_info"]').each(function(index, element){
            popover_content(self.$(element)).then(function($content){
                self.$(element).popover({
                    content: $content,
                    html: true,
                    placement: isRTL ? 'bottom' : 'left',
                    title: "Billing info",
                    trigger: 'focus',
                    delay: { "show": 0, "hide": 100 }
                })
            });
        });
        this.$el.find('i[data-role="purchase_method"]').popover();
    },
    load_orders: function(ev){
        this._value_filter(ev);
        this.load_order_lines();
    },
    _value_filter: function(ev){
        this.order_ids = ev.data.order_ids || [];
    },
    _prepare_function_reconcile_param: function(){
        var params = {}
        params.order_ids = this.order_ids;
        return params;
    },
    load_order_lines: function(){
        var self = this;
        var key_param = this._prepare_function_reconcile_param();
        this._rpc({
            model: 'invoice.purchase.order.line.reconcile.widget',
            method: 'get_purchase_order_line_for_invoice_reconcile',
            args: [self.invoice_id, self.mode],
            kwargs: key_param
        }).then(function (html) {
            self.$el.find('div#purchase_order_lines').html(html);
            self.prepare_info_popover();
        });
    },
    refresh_data: function(){
        var self = this;
        this.load_order_lines();
        this.load_invoice_view().then(()=>{
            self.render_invoice()
        });
    },
    select_all: function(ev){
        var self = this;
        // Retrieve the checked value
        var checked_value = this.$el.find(ev.target).prop('checked');
        this.$el.find('input.line_check').each((index, element)=>{
            self.$el.find(element).prop('checked', checked_value);
            self.$el.find(element).trigger('change');
        });
    },
    set_qty_to_reconcile: function(ev){
        var $input = this.$el.find(ev.target).closest('tr').find('input.o_field_float');
        var checked = this.$el.find(ev.target).prop('checked');
        if(checked) $input.val($input.data('value'));
        else $input.val(0);
    },
    reconcile: function(ev){
        ev.stopPropagation();
        var self = this;
        var data = this._serialize_data();
        // If no selection throw an error
        if(_.isEmpty(data)){
            this.do_warn(_t("Error on reconcile"), _t("Please, select at least one line to reconcile."));
            return
        }
        // calling method to reconcile order and in invoice
        this._rpc({
            model: 'invoice.purchase.order.line.reconcile.widget',
            method: 'reconcile_order_on_invoice',
            args: [data, self.invoice_id]
        }).then(function(res){
            self.$el.find('#refresh').trigger('click');
        });
    },
    unreconciled: function(ev){
        var self = this;
        var reconcile_id = $(ev.target).closest('button').data('reconcile-id');
        this._rpc({
            model: 'invoice.purchase.order.line.reconcile.widget',
            method: 'unreconcile_order_on_invoice',
            args: [reconcile_id]
        }).then(function(res){
            self.$el.find('#refresh').trigger('click');
        });
    },
    _serialize_data: function(){
        var params = [];
        var lines = this.$el.find('input.o_field_float').filter(function(){
            return parseFloat($(this).val()) > 0;
        });
        lines.closest('tr').each((i, tr)=>{
            var qty = parseFloat($(tr).find('input.o_field_float').val());
            if(isNaN(qty)) return;
            params.push({
                'order_line': parseInt($(tr).data('order-line-id')),
                'qty': parseFloat(qty),
            });
        });
        return params;
    }
});


core.action_registry.add('invoice_purchase_order_line_reconcile', invoiceOrderLineReconcileWidget);

return {
    invoiceOrderLineReconcileWidget: invoiceOrderLineReconcileWidget,
    FieldFilters: FieldFilters
};

});
