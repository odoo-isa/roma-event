# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from logging import getLogger

_logger = getLogger(__name__)


class L10nItEdiRelatedDocument(models.Model):
    _name = 'l10n_it_edi.related_document'
    _description = 'Related Documents'

    name = fields.Char(
        string='Document ID',
        size=20,
        required=True,
        copy=False
    )

    document_type = fields.Selection(
        string='Type',
        required=True,
        readonly=False,
        default=False,
        selection=[
            ('order', 'Order'),
            ('contract', 'Contract'),
            ('agreement', 'Agreement'),
            ('reception', 'Reception'),
            ('invoice', 'Related Invoice'),
            ('ddt', 'DDT')
        ],
        help="Indicates type that related document is associated",
        copy=False
    )

    date = fields.Date(
        string='Date',
        copy=False,
        help="Indicates date about related document"
    )

    code = fields.Char(
        string='Order Agreement Code',
        size=100,
        copy=False,
        help="Indicates code about related document"
    )

    cig = fields.Char(
        string='CIG',
        size=15,
        copy=False,
        help="Indicates cig about related document"
    )

    cup = fields.Char(
        string='CUP',
        size=15,
        copy=False,
        help="Indicates cup about related document"
    )

    move_id = fields.Many2one(
        string='Related Move',
        required=False,
        readonly=False,
        comodel_name='account.move',
        ondelete='cascade',
        copy=False,
        help="Indicates reference for associated move"
    )

    move_line_id = fields.Many2one(
        string='Related Move Line',
        required=False,
        readonly=False,
        comodel_name='account.move.line',
        ondelete='cascade',
        copy=False,
        help="Indicates reference for associated move line"
    )

    line_ref = fields.Integer(
        string='LineRef',
        size=4,
        required=False,
        readonly=True,
        related='move_line_id.sequence',
        default=0,
        help="Represents the reference to the move line",
        copy=False
    )

    num_item = fields.Integer(
        string='NumItem',
        size=20,
        required=False,
        readonly=False,
        default=0,
        help='Rapresents the reference to the line of an external document',
        copy=False
    )
