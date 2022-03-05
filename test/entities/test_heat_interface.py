# test_heat_interface.py

from draftsman.entity import HeatInterface, heat_interfaces
from draftsman.errors import InvalidEntityID, InvalidMode

from schema import SchemaError

from unittest import TestCase

class HeatInterfaceTesting(TestCase):
    def test_default_constructor(self):
        interface = HeatInterface()
        self.assertEqual(
            interface.to_dict(),
            {
                "name": "heat-interface",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_contstructor_init(self):
        interface = HeatInterface(
            temperature = 10,
            mode = "at-most"
        )
        self.assertEqual(
            interface.to_dict(),
            {
                "name": "heat-interface",
                "position": {"x": 0.5, "y": 0.5},
                "temperature": 10,
                "mode": "at-most"
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            HeatInterface(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            HeatInterface("this is not a heat interface")
        with self.assertRaises(SchemaError):
            HeatInterface(temperature = "incorrect")
        with self.assertRaises(AssertionError):
            HeatInterface(temperature = 100000)

    def test_set_temperature(self):
        interface = HeatInterface()
        interface.set_temperature(100)
        self.assertEqual(interface.temperature, 100)
        interface.set_temperature(None)
        self.assertEqual(interface.temperature, 0)
        with self.assertRaises(SchemaError):
            interface.set_temperature("incorrect")
        with self.assertRaises(AssertionError):
            interface.set_temperature(-1000)

    def test_set_mode(self):
        interface = HeatInterface()
        interface.set_mode("exactly")
        self.assertEqual(interface.mode, "exactly")
        interface.set_mode(None)
        self.assertEqual(interface.mode, "at-least")
        with self.assertRaises(InvalidMode):
            interface.set_mode("incorrect")