odoo.define('hw_l10n_it_cash_register.cash_register_ui', function (require) {
'use strict';

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var DeviceProxy = require('iot.widgets').DeviceProxy;

    var QWeb = core.qweb;
    var _t = core._t;

    var MicrelecHydraAction = AbstractAction.extend({
        events: {
            'keyup input[name^="payment"]': 'compute_payment_total',
            'click button[data-role="print-bill"]:not(.disabled)': 'confirmPrint',
            'click button[data-role="retry-print"]': 'retryPrint',
            'click div.cash-register:not(.offline, .active)': 'changeCashRegister',
        },
        template: 'CashRegisterInit',
        init: function(parent, action){
            this._super.apply(this, arguments);
            this.sale_order = action.params.sale_order; // Retrieve sale order
            this.precision = action.params.precision; // Get precision
            this.$cash_bill = null; // Variable with html contains cash bill template
            this.$cash_desk = null; // Variable with html contains cash desk template
        },
        willStart: function(){
            var self = this;
            return Promise.all([
                this._super.apply(this, arguments),
                this._prepare_cash_bill(),
                this._load_cash_desk(),
            ]);
        },
        _prepare_cash_bill: function(){
            let d = new $.Deferred();
            let self = this;
            // Call function to get html of sale order.
            this._rpc({
                model: 'sale.order',
                method: 'get_sale_order_cash_ticket',
                args: [[this.sale_order]],
            }).then(function(res){
                self.$cash_bill = res
                d.resolve();
            });
            return d.promise();
        },
        _load_cash_desk:function(){
            let d = new $.Deferred();
            let self = this;
            this._rpc({
                model: 'res.users',
                method: 'get_cash_desk_details',
                args: [[this.getSession().uid]]
            }).then(function(res){
                self.$cash_desk = QWeb.render("cashRegisterDesk", {
                    'cashes': res,
                    'active_user': self.getSession().uid
                });
                d.resolve();
            })
            return d.promise();
        },
        start: function(){
            this.$el.find('div#register').html(this.$cash_bill);
            this._render_cash_desk();
        },
        _render_cash_desk: function(){
            this.$el.find('div.cash-desk').html(this.$cash_desk);
        },
        compute_payment_total: function(ev){
            if(ev.keyCode === 13){
                return this.confirmPrint();
            }
            // Amount payment
            let amount_payment = this.get_amount_payment();
            // total
            let grand_total = this.$('span#grand_total').data('no-style-value');
            // Compute the change
            let change = amount_payment - grand_total;
            // Set this information value
            change = change.toFixed(this.precision);
            this.$('input[name="change"]').val(change >= 0 ? change: 0);
        },
        get_amount_payment: function(method='standard'){
            let amount_payment = $('input[name^="payment"]').map(
                (idx, elem)=>{return $(elem).val() && !$(elem).data('foregone') ? parseFloat($(elem).val()): 0}
            ).get().reduce((tot, elem) => {return tot + elem});
            // Foregone payment
            let foregone_payment = $('input[name^="payment"]').map(
                (idx, elem)=>{return $(elem).val() && $(elem).data('foregone') ? parseFloat($(elem).val()): 0}
            ).get().reduce((tot, elem) => {return tot + elem});
            if(method == 'standard') amount_payment -= foregone_payment;
            else if (method == 'sum') amount_payment += foregone_payment;
            else throw 'Invalid method parameter in get_amount_payment function !!';
            return amount_payment;
        },
        changeCashRegister: function(ev){
            let self = this;
            let $sel_cash = this.$(ev.target).closest('div.cash-register');
            let cur_user = $sel_cash.data('current-user');
            let cash_id = $sel_cash.data('cash-id');
            let confirm_change = true;
            // In case of the cash register is already busy from another user, ask for the confirmation.
            if(cur_user){
                confirm_change = confirm(_t(`Cash register is already busy from ${cur_user}. Do you want to continue?`));
            }
            if(!confirm_change) return;
            // call the cash register change
            this._rpc({
                model: 'res.users',
                method: 'change_default_cash_register',
                args: [[this.getSession().uid], cash_id]
            }).then(function(){
                self._load_cash_desk().then(()=>{self._render_cash_desk()});
            })
        },
        confirmPrint: function(){
            // Search for selected cash register
            let $sel_cash = this.$el.find('div.cash-register.active').not('.offline');
            if($sel_cash.length == 0){
                this.do_warn(_t("Error"), _t("No cash register specified. Please specify one from the top bar."));
                return;
            }
            // Check total congruency
            let grand_total = this.$('span#grand_total').data('no-style-value');
            let amount_payment = this.get_amount_payment('sum');
            if(amount_payment < grand_total){
                this.do_warn(_t("Error"), _t("Amount payment is different from grand total."));
                return;
            }
            // Execute printing
            this._executePrint($sel_cash);
        },
        retryPrint: function(){
            let $sel_cash = this.$el.find('div.cash-register.active').not('.offline');
            this._clear_message();
            this._printing_info(_t("Resend command print"));
            this.$el.find('button[data-role="retry-print"]').addClass("d-none");
            this._executePrint($sel_cash);
        },
        _executePrint: function($sel_cash){
            let d = new $.Deferred();
            let self = this;
            this.$el.find('#register').addClass('d-none');
            this.$el.find('.cash_printer').removeClass('d-none');
            this.$el.find('button[data-role="print-bill"]').addClass('disabled');
            this._printing_info(_t("Connect with the device"));
            //Retrieve print commands
            let payment_data = this.$el.find('input[name^="payment"]').filter(function(idx, el){
                return self.$(el).val();
            }).serializeArray();
            this._rpc({
                model: 'sale.order',
                method: 'get_print_bill_commands',
                args: [[this.sale_order], payment_data]
            }).then((data)=>{
                self._printing_success(_t("Create command to send to the device"));
                // Print receipt
                self._print_receipt($sel_cash, data);
                d.resolve();
            }).guardedCatch((error)=>{
                error.event.preventDefault();
                self._printing_error(error.message.data.message);
                d.resolve();
            })
            return d.promise()
        },
        _print_receipt: function($sel_cash, data){
            // Initialize the device
            let self = this;
            let iot_ip = $sel_cash.data('iot-ip');
            let identifier = $sel_cash.data('device-identifier');
            let iot_device = new DeviceProxy({
                iot_ip: iot_ip,
                identifier: identifier
            });
            // Prepare the IOT listener to get error message
            iot_device.add_listener(this._iot_message.bind(this));
            // Send command to print
            iot_device.action({
                command: data
            }).then(
                self._printing_complete.bind(this),
                self._printing_error.bind(this, "Unable to communicate with the device")
            );
        },
        _iot_message: function(message){
            if('error_message' in message){
                this._printing_error(message['error_message']);
            }
            else if('info_message' in message){
                this._printing_info(message['info_message']);
            }
            else if('warning_message' in message){
                this._printing_warning(message['warning_message']);
            }
            // Check if needed repeat command
            if('need_repeat' in message){
                this.$el.find('button[data-role="retry-print"]').removeClass("d-none");
            }
            // Check if receipt_number
            if('receipt_number' in message){
                this._rpc({
                    model: 'sale.order',
                    method: 'write',
                    args: [
                        [this.sale_order],
                        {
                            receipt_number: message['receipt_number'],
                            state: 'done'  //Order with cash bill goes in done state (locked)
                        }
                    ],
                });
            }
        },
        _printing_complete: function(){
            let message = _t("Printing complete.")
            let html_success = QWeb.render('cashRegisterSuccess', {'message': message});
            this.$el.find('.receipt').append(html_success);
            this.$el.find('.receipt').addClass('paused');
        },
        _printing_error: function(message){
            let html_error = QWeb.render('cashRegisterError', {'message': message});
            this.$el.find('.receipt').append(html_error);
            this.$el.find('.receipt').addClass('paused');
        },
        _printing_info: function(message){
            let html_info = QWeb.render('cashRegisterInfo', {'message': message});
            this.$el.find('.receipt').append(html_info);
        },
        _printing_warning: function(message){
            let html_warning = QWeb.render('cashRegisterWarning', {'message': message});
            this.$el.find('.receipt').append(html_warning);
        },
        _printing_success: function(message){
            let html_success = QWeb.render('cashRegisterSuccess', {'message': message});
            this.$el.find('.receipt').append(html_success);
        },
        _clear_message: function(){
            this.$el.find('.receipt').empty();
        }
    });

    // Register client action
    core.action_registry.add('micrelec_hydra_bill', MicrelecHydraAction);

    return {
        MicrelecHydraAction: MicrelecHydraAction
    };

});