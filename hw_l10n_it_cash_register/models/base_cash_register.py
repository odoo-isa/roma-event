# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from logging import getLogger

_logger = getLogger(__name__)


class BaseCashRegister(models.Model):
    _name = 'base.cash.register'
    _description = 'Cash register configuration'

    name = fields.Char(
        string='Cash name',
        help="Cash register name"
    )

    ip_address = fields.Char(
        string='Ip address',
        help='Ip address as configured in cash register settings',
        copy=False,
    )

    manufacturer = fields.Char(
        string='Manufacturer of the device',
        help='The device manufacturer',
        copy=False,
    )

    cash_model = fields.Selection(
        string='Cash register model',
        selection=[('hydra20', 'Hydra SF20')],
        help='The model of the cash register',
    )

    connection_type = fields.Selection(
        string='Connection type',
        selection=[('socket', 'Socket')],
        help='The connection type cash register interface',
        copy=True
    )

    connection_port = fields.Integer(
        string='Connection Port',
        required=False,
        default=0,
        help='Connection port. In case of socket the socket port, in case of TCP the TCP port.',
        copy=True,
    )

    iot_box_id = fields.Many2one(
        string='IOT Box',
        required=True,
        comodel_name='iot.box',
        ondelete="restrict",
        help="Linked IOT which manage this cash register",
        copy=False,
    )

    @api.constrains('ip_address')
    def _check_duplicated_ip_address(self):
        result = self.read_group([], ['ip_address'], ['ip_address'])
        for res in result:
            if res.get('ip_address_count', 0) >= 2:
                raise ValidationError(_("Cash Register cannot have same ip address"))
