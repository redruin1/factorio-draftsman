# test_power_switch.py

from draftsman.entity import PowerSwitch, power_switches
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class PowerSwitchTesting(TestCase):
    def test_default_constructor(self):
        switch = PowerSwitch()
        self.assertEqual(
            switch.to_dict(),
            {
                "name": "power-switch",
                "position": {"x": 1.0, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        switch = PowerSwitch(
            "power-switch", 
            position = [0, 0],
            switch_state = True
        )
        self.assertEqual(
            switch.to_dict(),
            {
                "name": "power-switch",
                "position": {"x": 1.0, "y": 1.0},
                "switch_state": True
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            PowerSwitch(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            PowerSwitch("this is not a power switch")

    def test_flags(self):
        for name in power_switches:
            power_switch = PowerSwitch(name)
            self.assertEqual(power_switch.power_connectable, True)
            self.assertEqual(power_switch.dual_power_connectable, True)
            self.assertEqual(power_switch.circuit_connectable, True)
            self.assertEqual(power_switch.dual_circuit_connectable, False)

    def test_dimensions(self):
        for name in power_switches:
            power_switch = PowerSwitch(name)
            self.assertEqual(power_switch.width, 2)
            self.assertEqual(power_switch.height, 2)