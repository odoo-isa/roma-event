# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
import werkzeug
from odoo.addons.base.models.ir_http import RequestUID
from odoo.http import request
from odoo import api, models


class MultiModelConverter(werkzeug.routing.BaseConverter):

    def __init__(self, url_map, model=False):
        super(MultiModelConverter, self).__init__(url_map)
        self.model = model
        self.regex = r'([0-9,]+)'

    def to_python(self, value):
        _uid = RequestUID(value=value, converter=self)
        env = api.Environment(request.cr, _uid, request.context)
        return env[self.model].browse(int(v) for v in value.split(','))

    def to_url(self, value):
        return "%s" % value


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_converters(cls):
        res = super(IrHttp, cls)._get_converters()
        res.update(multi_model=MultiModelConverter)
        return res
