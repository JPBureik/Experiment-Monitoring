#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 12:33:08 2021

@author: jp

Implements the abstract base class Sensor for experiment monitoring.

All interfaces for acquiring data should be subclasses that inherit from this
class.
"""

# Standard library imports:
from abc import ABC, abstractmethod
from influxdb import InfluxDBClient
import traceback

# Local imports
from exp_monitor.classes.database import Database


class Sensor(Database, ABC):

    def __init__(self, type, descr, unit, conversion_fctn, num_prec=None,
                 save_raw=False):
        self.type = type  # str
        self.descr = descr  # str
        self.unit = unit  # str
        self.conversion_fctn = conversion_fctn  # function_object
        self.num_prec = num_prec  # Set numerical precision
        self.save_raw = save_raw
        self._bounds = None  # {'lower': float, 'upper': float}
        self._filter_spikes = None  # float
        self._alert = None  # {'value': float, 'duration': float [min]}
        self._alert_cond = None  # {'value': float, 'duration': float [min]}
        # Database setup:
        super().__init__()

    @property
    def bounds(self):
        """Set bounds to limit the range of incoming measured values."""
        return self._bounds

    @bounds.setter
    def bounds(self, bounds):
        self._bounds = bounds

    @property
    def alert(self):
        """Set value and duration for automatic alerts."""
        return self._alert

    @alert.setter
    def alert(self, alert):
        self._alert = alert

    @property
    def filter_spikes(self):
        """Define method for spike filtering."""
        # 1) Get new measurement value
        # 2) Check that spike limits are defined, if not: default
        # 3) Compare to last measurement value
        # 4) Determine if spike
        # 5) If so, drop; if not, save
        pass

    @filter_spikes.setter
    def filter_spikes(self, filter_spikes):
        self._filter_spikes = filter_spikes

    @abstractmethod
    def connect(self):
        """Open the connection to the sensor."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the connection to the sensor."""
        pass

    @abstractmethod
    def rcv_vals(self):
        """Receive and return measurement values from sensor."""
        pass  # return received_vals

    def _show(self, show_raw=False):
        """Print last measurement with description and units."""
        try:
            if show_raw:
                print(self.descr, self.measurement, self.unit, ';\t raw:',
                      self.raw_vals)
            else:
                print(self.descr, self.measurement, self.unit)
        except AttributeError as ae:
            print(self.descr, '_show AttributeError:', ae.args[0])

    def _convert(self, rcv_vals):
        """Perform conversion of received values to proper unit."""
        try:
            # Account for specified numerical precision:
            """HOW TO FORMAT FLOAT IN SCIENTIFIC NOTATION NOT AS STRING?"""
            if self.num_prec:
                return round(self.conversion_fctn(rcv_vals), self.num_prec)
            else:
                return self.conversion_fctn(rcv_vals)
        except AttributeError:
            return None

    def measure(self, verbose=False, show_raw=False):
        """Execute a measurement."""
        try:
            self.connect()
            self.raw_vals = self.rcv_vals()
            self.measurement = self._convert(self.raw_vals)
            ## SPIKE FILTER
            ## CHECK SAVE RAW DATA
            if verbose:
                self._show(show_raw)
            self.disconnect()
        except Exception as e:
            print(self.descr, 'measurement error')
            traceback.print_exc()

    def to_db(self):
        """Write measurement result to database."""
        if self.save_raw:
            super().to_db(self.descr, self.unit, self.measurement,
                          self.save_raw, self.raw)
        else:
            super().to_db(self.descr, self.unit, self.measurement)
