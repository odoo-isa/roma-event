# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from logging import getLogger
from odoo import http
from odoo.http import request

_logger = getLogger(__name__)


class IoTControllerCashRegister(http.Controller):

    @http.route('/iot/get_cash_register_info', type='json', auth='public', methods=['POST'], csrf=False)
    def get_cash_register_info(self, **kwargs):
        """
        This route is an helper for cash register hydra driver.
        This api allow to the IOT to get information about configured cash register.
        For each of retrieved cash register will be check the connection directly
        on the IOT box driver
        :return: dictionary of available cash register for the iot device
        """
        _logger.info("Retrieve information about configured cash register")
        # Initialize the return variable
        available_cash = []
        # Search for the IOT BOX
        if kwargs:
            # Box > V19
            iot_device = kwargs['iot_device']
        else:
            # Box < V19
            data = request.jsonrequest
            iot_device = data['iot_device']
        mac = iot_device.get('mac', '')
        hostname = iot_device.get('hostname', '')
        # This two value are mandatory
        if not all([mac, hostname]):
            _logger.info("No mac address and hostname it was provided.")
            return available_cash
        box = request.env['iot.box'].sudo().search([
            ('name', '=', hostname),
            ('identifier', '=', mac)
        ], limit=1)
        if not box:
            _logger.warning(f"No IOT box founded with mac: {mac} and hostname: {hostname}")
            return available_cash
        for cash_register in box.available_cash_register_ids:
            available_cash.append({
                'name': cash_register.name,
                'ip_address': cash_register.ip_address,
                'model': cash_register.cash_model,
                'connection_type': cash_register.connection_type,
                'connection_port': cash_register.connection_port if cash_register.connection_port else 9101,
                'manufacturer': cash_register.manufacturer or 'n/a'
            })
        return available_cash
