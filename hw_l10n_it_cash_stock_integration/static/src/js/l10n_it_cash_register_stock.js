odoo.define('hw_l10n_it_cash_stock_integration.cash_register_stock_ui', function (require) {
'use strict';

    var MicrelecHydraAction = require('hw_l10n_it_cash_register.cash_register_ui').MicrelecHydraAction;

    var MicrelecHydraAction = MicrelecHydraAction.include({
        _printing_complete: function(){
            this._super.apply(this, arguments);
            // Validate picking
            this._rpc({
                model: 'sale.order',
                method: 'transfer_sale_picking',
                args: [[this.sale_order]]
            });
        }
    });

})
