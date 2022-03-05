# test_electric_energy_interface.py

from draftsman.entity import ElectricEnergyInterface, electric_energy_interfaces
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class ElectricEnergyInterfaceTesting(TestCase):
    def test_default_constructor(self):
        interface = ElectricEnergyInterface()
        self.assertEqual(
            interface.to_dict(),
            {
                "name": "electric-energy-interface",
                "position": {"x": 1.0, "y": 1.0}
            }
        )

    def test_contstructor_init(self):
        interface = ElectricEnergyInterface(
            buffer_size = 10000,
            power_production = 10000,
            power_usage = 0
        )
        self.assertEqual(
            interface.to_dict(),
            {
                "name": "electric-energy-interface",
                "position": {"x": 1.0, "y": 1.0},
                "buffer_size": 10000,
                "power_production": 10000,
                "power_usage": 0
            }
        )

        with self.assertWarns(UserWarning):
            ElectricEnergyInterface(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            ElectricEnergyInterface("this is not an electric energy interface")

    def test_set_buffer_size(self):
        interface = ElectricEnergyInterface()
        interface.set_buffer_size(100)
        self.assertEqual(interface.buffer_size, 100)
        interface.set_buffer_size(None)
        self.assertEqual(interface.buffer_size, None)
        with self.assertRaises(SchemaError):
            interface.set_buffer_size("incorrect")

    def test_set_power_production(self):
        interface = ElectricEnergyInterface()
        interface.set_power_production(100)
        self.assertEqual(interface.power_production, 100)
        interface.set_power_production(None)
        self.assertEqual(interface.power_production, None)
        with self.assertRaises(SchemaError):
            interface.set_power_production("incorrect")

    def test_set_power_usage(self):
        interface = ElectricEnergyInterface()
        interface.set_power_usage(100)
        self.assertEqual(interface.power_usage, 100)
        interface.set_power_usage(None)
        self.assertEqual(interface.power_usage, None)
        with self.assertRaises(SchemaError):
            interface.set_power_usage("incorrect")