# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    default_cash_device = fields.Many2one(
        string='Default cash register',
        comodel_name='base.cash.register',
        ondelete="set null",
        help="Set the default cash register device for this user",
        copy=False,
    )

    related_department_iot_box = fields.Many2one(
        string='Related IOT box',
        comodel_name='iot.box',
        related='department_id.iot_box_id'
    )

    @api.onchange('department_id')
    def _onchange_department_iot(self):
        self.default_cash_device = None

    def get_cash_desk_details(self) -> {}:
        """
        Retrieve information about cash register enable for this user.
        The available cash register are retrieved by the iot.box linked to the user department.
        This function return also if the cash register is a default for a specific user and if it is connected or not.
        :return: dictionary
        """
        self.ensure_one()
        res = {}
        iot_box = self.department_id.iot_box_id
        if not iot_box:
            return res
        # From the Iot Box retrieve all available cash register
        for cash_register in iot_box.available_cash_register_ids:
            # Search for associated device, otherwise is not a valid cash register
            device_identifier = f"{cash_register.cash_model}:{cash_register.ip_address}"
            device = self.env['iot.device'].search([
                ('identifier', '=', device_identifier)
            ], limit=1)
            if not device:
                _logger.warning(f"The device identifier {device_identifier} not exists as real device")
                continue
            res[cash_register.id] = {
                'name': cash_register.name,
                'model': cash_register.cash_model,
                'ip': cash_register.ip_address,
                'device_identifier': device.identifier,
                'device': device.id,
                'device_status': device.connected,
                'user': (False, False),
                'iot_ip': iot_box.ip
            }
            # Check if the device is default for a specific user
            user = self.env['res.users'].search([
                ('default_cash_device', '=', cash_register.id)
            ], limit=1)
            if user:
                res[cash_register.id].update({
                    'user': (user.id, user.name)
                })
        return res

    def change_default_cash_register(self, cash_id):
        """
        Set the cash_id as default for the current user. Empty for the other one.
        :param cash_id: the default cash_id to set
        :return: void
        """
        self.ensure_one()
        # Search if the cash register is already set for another user
        self = self.sudo()
        already_busy = self.env['res.users'].search([
            ('default_cash_device', '=', cash_id)
        ])
        if already_busy:
            already_busy.write({
                'default_cash_device': False
            })
        # Set the device for current user
        self.default_cash_device = cash_id
