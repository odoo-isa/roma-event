# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
import base64
from odoo.tools.translate import _
from odoo.addons.http_routing.models.ir_http import slugify


class FileExportWizard(models.TransientModel):
    _name = "file.export.wizard"
    _description = "File export wizard"

    riba_txt = fields.Binary(
        string='Bank Paper Txt',
        readonly=True,
        help="It is necessary to download riba txt file",
        attachment=True,
        copy=False
    )

    filename = fields.Char(
        string='Filename'
    )
