odoo.define('purchase_order_invoice_reconciliation_stock_integration.reconciliation_ddt', function(require){
'use strict';

var reconciliationWidget = require('purchase_order_invoice_reconciliation.reconciliation').invoiceOrderLineReconcileWidget;
var core = require('web.core');

var _t = core._t;


var invoiceOrderLineReconcileWidget = reconciliationWidget.include({
    init: function(parent, action){
        this._super.apply(this, arguments);
        this.ddt_ids = "";
    },
    adding_filter_fields: function(){
        var fields = this._super();
        fields['ddt_ids'] = {
            label: _t('DdT (split by ; if more than one)'),
            type: 'char',
        }
        return fields;
    },
    _value_filter: function(ev){
        this._super.apply(this, arguments);
        this.ddt_ids = ev.data.ddt_ids || "";
    },
    _prepare_function_reconcile_param: function(){
        var params = this._super.apply(this, arguments);
        params.ddt_ids = this.ddt_ids;
        return params;
    }
});

});