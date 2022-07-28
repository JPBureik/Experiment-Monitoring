#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:15:51 2022

@author: jp
"""

# Standard library imports:


# Local imports:
from expmonitor.classes.sensor import Sensor
from expmonitor.utility import img_proc


class Webcam(Sensor):

    def __init__(self, descr):
        # General sensor setup:
        self.type = 'Vacuum Gauge'
        self.descr = descr.replace(' ', '_').lower() + '_vac'  # Multi-word
        self.unit = 'mbar'
        self.conversion_fctn = lambda t: t  # No conversion needed
        super().__init__(
            self.type, self.descr, self.unit, self.conversion_fctn, num_prec=1
            )
        # Phidget-specific setup:
        self.savepath = r'/mnt/data/webcam/zeeman2/z2.png'

    def connect(self):
        # Not needed:
        pass

    def disconnect(self):
        # Not needed:
        pass

    def rcv_vals(self):
        # Receive temperature value:
        return img_proc(self.savepath)


# Execution:
if __name__ == '__main__':

    from exp_monitor.config import *
    Webcam.test_execution()