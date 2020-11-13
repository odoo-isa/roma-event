odoo.define('l10n_it.edi.extension.isa.upload.bill', function(require){
"use strict;";

    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    var UploadBillMixinFromWizard = {

        start: function () {
            this.fileUploadID = _.uniqueId('account_bill_file_upload_from_wizard');
            return this._super.apply(this, arguments);
        },
    }

    return UploadBillMixinFromWizard;
});

odoo.define('l10n_it.edi.extension.isa.upload.bill.tree', function(require){
"use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var UploadBillMixinFromWizard = require('l10n_it.edi.extension.isa.upload.bill');
    var viewRegistry = require('web.view_registry');
    var _t = core._t;

    var BillsListControllerWizard = ListController.extend(UploadBillMixinFromWizard, {
        buttons_template: 'BillsListView.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_button_upload_bill_from_wizard': '_onUpload',
        }),
        _onUpload: function (event) {
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window',
                name: _t('Add Attachment'),
                res_model: 'account.invoice.import.wizard',
                views: [[false, "tree"], [false, "form"]],
                context: self._context,
                target: 'new'
            });
        },
    });

    var BillsListViewWizard = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: BillsListControllerWizard,
        }),
    });

    viewRegistry.add('account_tree', BillsListViewWizard);

});