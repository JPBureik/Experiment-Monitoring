#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 10:54:18 2021

@author: jp

Implements the ArduinoADC Class for experiment monitoring.

This module reads out all 12 Analog Input signals sent from the Arduino over
TCP/IP and returns them as floats in a list.

The entries of the list correspond to the Analog Inputs in ascending order,
i.e. A0 through A11.

Note that it always returns a list of length 12, regardless of how many Analog
Inputs are used. The unused analog pins will float, so be sure to correctly
identify the signals to be monitored.
"""

# Standard library imports:
import socket
import time

# Local imports:
from exp_monitor.classes.sensor import Sensor


class ArduinoADC(Sensor):

    def __init__(self):
        self.type = 'ADC'
        self.descr = 'Arduino Analog-to-Digital Converter'
        self.unit = 'V'
        self.buffer_size = 2**12
        self.volt_limit = 3.25
        self.numerical_precision = 3
        self.conversion_fctn = lambda v_int: v_int / self.buffer_size * self.volt_limit
        super().__init__(self.type, self.descr, self.unit, self.conversion_fctn)
        self.IP = '10.117.53.45'  # Static IP: IOGS network
        #self.IP = '172.20.217.9' # DHCP: Visitor network - not recommended
        self.port = 6574  # Match to server side port
        self.analog_signals = {}

    def connect(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.connect((self.IP, self.port))
        self.soc.sendall(b'a')  # Send a non-empty message to initialize TCP/IP com

    def measure(self):
        self.connect()
        # Measurement data: 12-bit int -> receive msg as 2**8 * byte1 + byte2
        for channel in range(12):
            # Receive both bytes successively:
            byte1 = self.soc.recv(self.buffer_size)
            byte2 = self.soc.recv(self.buffer_size)
            # Restore original 12-bit integer:
            v_int = 2**8*(int.from_bytes(byte1, 'little')) +\
                int.from_bytes(byte2, 'little')
            # Limit to Arduino voltage range to filter badly converted values:
            v = round(self.conversion_fctn(v_int), self.numerical_precision)
            self.analog_signals[channel] = v if 0 <= v <= self.volt_limit else None
        self.disconnect()
        # Buffer time for Arduino:
        time.sleep(0.1)
        return self.analog_signals

    def disconnect(self):
        self.soc.shutdown(socket.SHUT_RDWR)
        self.soc.close()


# Execution:
if __name__ == '__main__':

    arduino_adc = ArduinoADC()
    analog_signals = arduino_adc.measure()
    for ai_channel in range(12):
        print('Channel', ai_channel, '\t', analog_signals[ai_channel], 'V')