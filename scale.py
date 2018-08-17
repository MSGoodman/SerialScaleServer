"""
This module provides the SerialScaleReader object.
It can be used to:
    - Send a command to a scale and receive a response back
    - Update the serial port settings for the scale
"""
import time
import serial
from serial.tools import list_ports

PARITY_OPTIONS = {
    'none': serial.PARITY_NONE,
    'odd': serial.PARITY_ODD,
    'even': serial.PARITY_EVEN,
    'mark': serial.PARITY_MARK,
    'space': serial.PARITY_SPACE
}

STOP_BITS_OPTIONS = {
    1: serial.STOPBITS_ONE,
    1.5: serial.STOPBITS_ONE_POINT_FIVE,
    2: serial.STOPBITS_TWO
}

BYTE_SIZE_OPTIONS = {
    5: serial.FIVEBITS,
    6: serial.SIXBITS,
    7: serial.SEVENBITS,
    8: serial.EIGHTBITS,
}

class SerialScaleReader():
    """ Handles a serial-port scale by sending and receiving data """
    def __init__(self, wait_interval_seconds=0.25, max_wait_time_seconds=1.5, read_weight_command=b'W\r', end_of_weight_char=b'\x03', port='COM1', baud_rate=9600, parity=serial.PARITY_EVEN, stop_bits=serial.STOPBITS_ONE, byte_size=serial.SEVENBITS):
        # Wait times for reading from the scale
        self.wait_time = 0
        self.wait_interval_seconds = wait_interval_seconds # I chose this arbitrarily
        self.max_wait_time_seconds = max_wait_time_seconds # Defaults to 1.5 seconds because any longer would annoy me

        # Scale protocol details
        self.read_weight_command = read_weight_command # Default, b'W\r', is the standard for NCI scales
        self.end_of_weight_char = end_of_weight_char # Default, b'\x03', is the standard for NCI scales

        # Scale properties
        self.serial_reader = serial.Serial()
        self.serial_reader.port = port # Defaults to COM1
        self.serial_reader.baud_rate = baud_rate # 9600 seems to be a typical baud rate
        self.serial_reader.parity = parity # Defaults to even since NCI scales use this
        self.serial_reader.stop_bits = stop_bits # Defaults to one since NCI scales use this
        self.serial_reader.bytesize = byte_size # Defaults to seven since NCI scales use this

    def get_settings(self):
        """ Retrieve settings for the serial port reader """
        # Stuff to return
        return_dict = {
            'port': self.serial_reader.port,
            'baud_rate': self.serial_reader.baud_rate,
            'parity': self.serial_reader.parity,
            'stop_bits': self.serial_reader.stop_bits,
            'byte_size': self.serial_reader.bytesize,
        }
        return return_dict

    def update_settings(self, **kwargs):
        """ Update settings for the serial port reader and return any errors encountered in doing so"""
        setting_errors = {}

        # Port
        port = kwargs.get('port')
        if port:
            if list(list_ports.grep(port)):
                self.serial_reader.port = port
            else:
                setting_errors['port'] = {
                    'given_value': port,
                    'error': 'Invalid port. Detected ports: {}'.format(
                        ', '.join([port.device for port in list_ports.comports()])
                    )
                }

        # Baud Rate
        baud_rate = kwargs.get('baud_rate')
        if baud_rate:
            try:
                self.serial_reader.baud_rate = int(baud_rate)
            except (TypeError, ValueError):
                setting_errors['baud_rate'] = {
                    'given_value': baud_rate,
                    'error': 'Baud rate must be integer'
                }

        # Parity
        parity = kwargs.get('parity')
        if parity:
            parity = parity.lower()
            if parity in PARITY_OPTIONS:
                self.serial_reader.parity = PARITY_OPTIONS[parity]
            else:
                setting_errors['parity'] = {
                    'given_value': parity,
                    'error': 'Parity must be one of the following: {}'.format(
                        ', '.join("'{}'".format(key) for key in PARITY_OPTIONS)
                    )
                }

        # Stop Bits
        stop_bits = kwargs.get('stop_bits')
        if stop_bits:
            try:
                stop_bits = float(stop_bits)
            except (TypeError, ValueError):
                pass
            if stop_bits in STOP_BITS_OPTIONS:
                self.serial_reader.stop_bits = STOP_BITS_OPTIONS[stop_bits]
            else:
                setting_errors['stop_bits'] = {
                    'given_value': stop_bits,
                    'error': 'Stop bits must be one of the following: {}'.format(
                        ', '.join(str(key) for key in STOP_BITS_OPTIONS)
                    )
                }

        # Byte Size
        byte_size = kwargs.get('byte_size')
        if byte_size:
            try:
                byte_size = int(byte_size)
            except (TypeError, ValueError):
                pass
            if byte_size in BYTE_SIZE_OPTIONS:
                self.serial_reader.bytesize = BYTE_SIZE_OPTIONS[byte_size]
            else:
                setting_errors['byte_size'] = {
                    'given_value': byte_size,
                    'error': 'Byte size must be one of the following: {}'.format(
                        ', '.join(str(key) for key in BYTE_SIZE_OPTIONS)
                    )
                }

        return setting_errors

    def update_and_get_settings(self, **kwargs):
        """ Update and retrieve settings for the serial port reader, as well as any errors encountered in updating """
        return {'errors': self.update_settings(**kwargs), 'settings': self.get_settings()}

    def read_weight(self):
        """ Send a read command to the scale and wait for a response to return """
        try:
            with self.serial_reader as open_reader:
                # Write weight command
                scale_output = ''
                open_reader.write(self.read_weight_command)

                while True:
                    # Handle wait-times
                    if self.wait_time > self.max_wait_time_seconds:
                        self.wait_time = 0
                        return 'Scale response took too long, check connection and reconsider max_wait_time_seconds'
                    time.sleep(self.wait_interval_seconds)
                    self.wait_time += self.wait_interval_seconds

                    # Read everything in buffer
                    print(open_reader)
                    while open_reader.in_waiting > 0:
                        this_byte = open_reader.read(1)
                        if this_byte == self.end_of_weight_char:
                            return scale_output
                        scale_output += this_byte.decode("utf-8")
        except serial.serialutil.SerialException as err:
            return 'Error: {}'.format(err)
