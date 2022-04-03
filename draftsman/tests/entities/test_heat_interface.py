# test_heat_interface.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import HeatInterface, heat_interfaces
from draftsman.error import InvalidEntityError, InvalidModeError
from draftsman.warning import DraftsmanWarning, TemperatureRangeWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class HeatInterfaceTesting(TestCase):
    def test_contstructor_init(self):
        interface = HeatInterface(temperature=10, mode="at-most")
        self.assertEqual(
            interface.to_dict(),
            {
                "name": "heat-interface",
                "position": {"x": 0.5, "y": 0.5},
                "temperature": 10,
                "mode": "at-most",
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            HeatInterface(unused_keyword="whatever")
        with self.assertWarns(TemperatureRangeWarning):
            HeatInterface(temperature=100000)  # 100,000

        # Errors
        with self.assertRaises(InvalidEntityError):
            HeatInterface("this is not a heat interface")
        with self.assertRaises(TypeError):
            HeatInterface(temperature="incorrect")

    def test_set_temperature(self):
        interface = HeatInterface()
        interface.temperature = 100
        self.assertEqual(interface.temperature, 100)
        interface.temperature = None
        self.assertEqual(interface.temperature, None)
        # Warnings
        with self.assertWarns(TemperatureRangeWarning):
            interface.temperature = -1000
        # Errors
        with self.assertRaises(TypeError):
            interface.temperature = "incorrect"

    def test_set_mode(self):
        interface = HeatInterface()
        interface.mode = "exactly"
        self.assertEqual(interface.mode, "exactly")
        interface.mode = None
        self.assertEqual(interface.mode, None)
        with self.assertRaises(InvalidModeError):
            interface.mode = "incorrect"
