# -*- coding: utf-8 -*-

import logging
import time
import socket
import urllib3
import json
import traceback
from threading import Thread
from odoo.tools.translate import _
from odoo.addons.hw_drivers.tools import helpers
from odoo.addons.hw_drivers.controllers.driver import event_manager
from odoo.addons.hw_drivers.controllers.driver import socket_devices, m, IoTDevice, Driver


_logger = logging.getLogger(__name__)


class HydraDriver(Driver):
    connection_type = 'network'

    def __init__(self, device):
        super(HydraDriver, self).__init__(device)
        self._device_type = 'device'
        self._device_connection = 'network'
        self._device_manufacturer = self.dev['manufacturer']
        self._device_name = self.dev['name']

    @property
    def device_identifier(self):
        return self.dev['identifier']

    def action(self, data):
        commands = data.get('command', False)
        if not commands:
            return  # todo
        ip = self.dev['ip_address']
        port = self.dev['connection_port']
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            for command in commands:
                s.sendall(bytes(command, 'utf-8'))
                socket_resp = s.recv(1024)
                # Manage the response
                socket_resp = socket_resp.decode('utf-8')
                resp_code, dev_status, fiscal_status, *other = socket_resp.split('/')
                # Check the replay code
                next_command = self._check_replay_code(resp_code, s)
                if not next_command:
                    s.sendall(bytes('+/0/', 'utf-8'))
                    break
                # Check the device status.
                next_command = self._check_device_status(dev_status)
                if not next_command:
                    s.sendall(bytes('+/0/', 'utf-8'))
                    break
                # if Command is 0/ search for receipt number to store.
                if command == '0/':
                    receipt_number = other[6]
                    self.data = {
                        'info_message': _("Number of receipt %s") % receipt_number,
                        'receipt_number': int(receipt_number)
                    }
                    event_manager.device_changed(self)
        except Exception as e:
            _logger.error(f"Error on socket communication: {e}")
            pass

    def _check_device_status(self, dev_status):
        """
        Check the device status and return if available next command
        :param dev_status: the device status to check
        :return: bool available for next command or exit.
        """
        repeat_command, need_restart, need_service, message = self._get_device_status(dev_status)
        if repeat_command:
            self.data = {
                'info_message': message,
                'need_repeat': True
            }
            event_manager.device_changed(self)
            next_command = False
        elif need_restart:
            self.data = {
                'warning_message': message
            }
            next_command = False
            event_manager.device_changed(self)
        elif need_service:
            self.data = {
                'error_message': message
            }
            next_command = False
            event_manager.device_changed(self)
        else:
            # Everything is ok
            next_command = True
        return next_command

    def _get_device_status(self, dev_status):
        """
        This function it is used to check the device status.
        Some status are critical and must terminate command, other status (such as busy device) indicate that have to be
        repeat command.
        MSB                                                                                                                                                     LSB
        +--------------+-----------------+------------------------+-----------------+------------------+---------------+-------------------------+----------------+
        |    BIT 7     |      BIT 6      |         BIT 5          |      BIT 4      |      BIT 3       |     BIT 2     |          BIT 1          |     BIT 0      |
        +--------------+-----------------+------------------------+-----------------+------------------+---------------+-------------------------+----------------+
        | Cutter Error | Printer timeout | Fiscal File Full       | Printer Offline | Battery Warning  | Paper End     | Fatal Error             | Device busy    |
        | 1 = Error    | 1 = Error       | 1 = Memory daily limit | 1 = Offline     | 1 = Need service | 1 = End paper | 1 = Error. Need service | 1 = Busy retry |
        +--------------+-----------------+------------------------+-----------------+------------------+---------------+-------------------------+----------------+
        :param dev_status: the dev status is rappresent by two char rapresent HEX value. This HEX value have to be
        converted in bit (with padding zero) and check each bit based to the top table
        :return: tuple:
        repeat_command -> the command will be repeat after 20 second
        need_restart -> the command execution will be interrupted and will be send a message to the user to ask for
        restart the device and repeat command (manually)
        need_service -> the command will be interrupted and user will be notify with a critical message (need service)
        message -> the message to send to the user
        """
        # Mapping message
        bit_dev_message = {
            0: _('Device Busy. Please check the device monitor.'),
            1: _('Fatal Error on the device. Need service.'),
            2: _('Paper end. Please change paper.'),
            3: _('Battery Warning. Please turn off device and retry.'),
            4: _('Printer Offline. Please turn off device and retry.'),
            5: _('Fiscal File Full. Daily data exceed the maximum limit. Need service.'),
            6: _('Printer Timeout. Please turn off device and retry.'),
            7: _('Cutter Error. Please turn off device and retry.'),
        }
        # This is the returning variable.
        message = None
        repeat_command, need_restart, need_service = 0, 0, 0
        h_size = len(dev_status) * 4  # each hex digits translate to 4 bit
        dev_status = (bin(int(dev_status, 16))[2:]).zfill(h_size)  # Convert to binary with zero fill
        dev_status = dev_status[::-1]  # Reverse the string because have to elaborate from less to more significant bit
        for bit_pos, bit_value in enumerate(dev_status):
            bit_value = int(bit_value)
            if bit_value == 0:
                continue  # If bit value is zero means that there isn't no error
            # Check the position (only bit0 and bit2) need replay command, the other set error status on the device
            # or need cash restart or service.
            if bit_pos in (0, 2):
                repeat_command = 1
            elif bit_pos in (1, 5):
                need_service = 1
            else:
                need_restart = 1
            # Retrieve the message
            message = bit_dev_message[bit_pos]
            break
        return repeat_command, need_restart, need_service, message

    def _check_replay_code(self, resp_code, s) -> bool:
        # This field contains the error in HEXADECIMAL value /!\ Attention. Not in decimal.
        # In this function are not managed all error. Only the most important.
        # convert to decimal
        resp_code = int(resp_code, 16)
        hydra_error = {
            9: _('Wrong VAT Value. Please check the VAT department configuration'),
            12: _("The payment code doesn't exist. Please check payment configuration."),
            15: _("Printing type error."),
            16: _("The day is open, issue a Z- report first."),
            18: _("Wrong TIME, not allowed operation."),
            19: _("CAN NOT PERFORM SALES."),
            20: _("A transaction is open, close the transaction first."),
            21: _("Receipt in Payment."),
            22: _("Cash in/out transaction in progress."),
            23: _("Wrong VAT rate."),
            24: _("Price Error."),
            26: _("The ECR is busy, try again later."),
            27: _("Invalid sales operation."),
            28: _("Invalid Discount/Markup type."),
            44: _("Paper End."),
            45: _("Error with the cutter."),
            46: _("The printer is disconnected."),
            51: _("The printer cover is open."),
            60: _("Fiscal memory is full."),
            61: _("Larger quantity value than the one allowed."),
            62: _("Inactive payment type."),
            65: _("Please provide zeroing command to close fiscal daily"),
            67: _("Discount/markup limit exceeded."),
            68: _("Zero discount/markup."),
            77: _("Change is not allowed for this payment type."),
            78: _("Must insert the payment amount."),
            84: _("Negative receipt total."),
            85: _("Receipt sales amount exceeded."),
        }
        if resp_code == 0:
            return True
        # Check for the error
        if resp_code in hydra_error:
            error_message = hydra_error[resp_code]
        else:
            error_message = _("Generic error message. Please communicate this number to the support: %s") % resp_code
        # Send the message back to the Odoo
        self.data = {
            'error_message': error_message,
        }
        # If enable retry button in the user interface
        if resp_code in (26, 44, 51):
            self.data['need_repeat'] = True
        event_manager.device_changed(self)
        return False

    @classmethod
    def supported(cls, device):
        # If the device is not a dictionary (Eg. is an object) return as not supported
        if type(device) != dict:
            return False
        # Check the model and the connection type
        cash_model = device.get('model', None)
        connection_type = device.get('connection_type', None)
        if cash_model == 'hydra20' and connection_type == 'socket':
            return True
        return False


# Must waiting for main thread started. The main thread (Manager class inside hw_drivers/controller/driver) is in
# charge for discover new device. The only way to adding new device is to pass trough socket_device that is a
# variable declare globally.
while not m.is_alive():
    time.sleep(1)


# At this point the Manager thread is active and running. We have to launch new thread that refresh all available
# cash register related to this specific IOT
class HydraCashManager(Thread):

    def _discover_n_adding_hydra20_device(self, cash_register):
        if not cash_register:
            return
        # Create the cash identifier
        cash_identifier = f"{cash_register['model']}:{cash_register['ip_address']}"
        # Try to connect to the device (only socket is accepted)
        if cash_register['connection_type'] != 'socket':
            _logger.error(
                f"For this device only socket connection is enabled. Device type {cash_register['connection_type']}"
            )
            # if cash register is in device list have to be removed
            if cash_identifier in socket_devices:
                del socket_devices[cash_identifier]
            return
        # Try to connect to socket
        s = None
        try:
            ip = cash_register['ip_address']
            port = cash_register['connection_port']
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)  # Wait only half second if no response means that the device is no available
            s.connect((ip, port))
            s.sendall(b'a')  # Send the command to retrieve ECR identification
            s.recv(1024)
            # Create the IOT device and adding to the available device
            cash_register_device = IoTDevice({
                'identifier': cash_identifier,
                'name': cash_register['name'],
                'model': cash_register['model'],
                'connection_type': cash_register['connection_type'],
                'manufacturer': cash_register['manufacturer'],
                'ip_address': cash_register['ip_address'],
                'connection_port': cash_register['connection_port']
            }, 'network')
            # Adding the device to socket_devices
            socket_devices[cash_identifier] = cash_register_device
        except (ValueError, socket.timeout):
            # If device is not ready (and it is in available device) have to remove it
            if cash_identifier in socket_devices:
                del socket_devices[cash_identifier]
        finally:
            # Close the socket connection
            if s:
                s.close()

    def _retrieve_cash_info_from_sever(self):
        # Retrieve the IOT BOX information
        iot_data = {
            'mac': helpers.get_mac_address(),
            'hostname': socket.gethostname()
        }
        # Retrieve the odoo server
        while 1:
            odoo_server = helpers.get_odoo_server_url()
            if not odoo_server:
                _logger.warning('Odoo server not set')
                time.sleep(10)  # Wait ten seconds before to check for odoo server
                continue
            # disable certificate verification
            urllib3.disable_warnings()
            http = urllib3.PoolManager(cert_reqs='CERT_NONE')
            # Contact Odoo server in order to retrieve the cash registers configuration
            try:
                encoded_body = json.dumps({
                    'iot_device': iot_data
                })
                req = http.request(
                    'POST',
                    f"{odoo_server}/iot/get_cash_register_info",
                    body=encoded_body,
                    headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
                )
                data = req.data.decode('utf-8')
                data = json.loads(data)
                result = data['result']
                return result
            except Exception as e:
                _logger.error(f"Hydra gathering information error: {traceback.format_exc()}")
                _logger.error('Could not reach configured server')
                _logger.error('A error encountered : %s ' % e)
                time.sleep(10)  # Try after ten seconds

    def run(self) -> None:
        # Retrieve information about cash register at the startup
        result = self._retrieve_cash_info_from_sever()
        while 1:
            # Adding the device
            for cash_register in result:
                if cash_register['model'] == 'hydra20':
                    self._discover_n_adding_hydra20_device(cash_register)
                else:
                    _logger.error(f"the cash register model {cash_register['model']} isn't sill already supported.")
            time.sleep(3)


hydra_manager = HydraCashManager()
hydra_manager.daemon = True
hydra_manager.start()
