# test_power_switch.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import PowerSwitch, power_switches
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class PowerSwitchTesting(TestCase):
    def test_constructor_init(self):
        switch = PowerSwitch("power-switch", tile_position=[0, 0], switch_state=True)
        self.assertEqual(
            switch.to_dict(),
            {
                "name": "power-switch",
                "position": {"x": 1.0, "y": 1.0},
                "switch_state": True,
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            PowerSwitch(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            PowerSwitch("this is not a power switch")

    def test_flags(self):
        for name in power_switches:
            power_switch = PowerSwitch(name)
            self.assertEqual(power_switch.power_connectable, True)
            self.assertEqual(power_switch.dual_power_connectable, True)
            self.assertEqual(power_switch.circuit_connectable, True)
            self.assertEqual(power_switch.dual_circuit_connectable, False)

    def test_switch_state(self):
        power_switch = PowerSwitch()
        power_switch.switch_state = False
        self.assertEqual(power_switch.switch_state, False)
        power_switch.switch_state = None
        self.assertEqual(power_switch.switch_state, None)
        with self.assertRaises(TypeError):
            power_switch.switch_state = TypeError
