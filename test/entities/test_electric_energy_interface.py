# test_electric_energy_interface.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import ElectricEnergyInterface, electric_energy_interfaces
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class ElectricEnergyInterfaceTesting(TestCase):
    def test_contstructor_init(self):
        interface = ElectricEnergyInterface(
            "electric-energy-interface",
            buffer_size=10000,
            power_production=10000,
            power_usage=0,
        )
        self.assertEqual(
            interface.to_dict(),
            {
                "name": "electric-energy-interface",
                "position": {"x": 1.0, "y": 1.0},
                "buffer_size": 10000,
                "power_production": 10000,
                "power_usage": 0,
            },
        )

        with self.assertWarns(DraftsmanWarning):
            ElectricEnergyInterface(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            ElectricEnergyInterface("this is not an electric energy interface")

    def test_set_buffer_size(self):
        interface = ElectricEnergyInterface()
        interface.buffer_size = 100
        self.assertEqual(interface.buffer_size, 100)
        interface.buffer_size = None
        self.assertEqual(interface.buffer_size, None)
        with self.assertRaises(TypeError):
            interface.buffer_size = "incorrect"

    def test_set_power_production(self):
        interface = ElectricEnergyInterface()
        interface.power_production = 100
        self.assertEqual(interface.power_production, 100)
        interface.power_production = None
        self.assertEqual(interface.power_production, None)
        with self.assertRaises(TypeError):
            interface.power_production = "incorrect"

    def test_set_power_usage(self):
        interface = ElectricEnergyInterface()
        interface.power_usage = 100
        self.assertEqual(interface.power_usage, 100)
        interface.power_usage = None
        self.assertEqual(interface.power_usage, None)
        with self.assertRaises(TypeError):
            interface.power_usage = "incorrect"
