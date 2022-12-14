# test_power_switch.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.entity import PowerSwitch, power_switches
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class PowerSwitchTesting(unittest.TestCase):
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
        with self.assertRaises(DataFormatError):
            PowerSwitch(control_behavior={"unused_key": "something"})

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

    def test_mergable_with(self):
        switch1 = PowerSwitch("power-switch")
        switch2 = PowerSwitch("power-switch", switch_state=True, tags={"some": "stuff"})

        self.assertTrue(switch1.mergable_with(switch1))

        self.assertTrue(switch1.mergable_with(switch2))
        self.assertTrue(switch2.mergable_with(switch1))

        switch2.tile_position = (1, 1)
        self.assertFalse(switch1.mergable_with(switch2))

    def test_merge(self):
        switch1 = PowerSwitch("power-switch")
        switch2 = PowerSwitch("power-switch", switch_state=True, tags={"some": "stuff"})

        switch1.merge(switch2)
        del switch2

        self.assertEqual(switch1.switch_state, True)
        self.assertEqual(switch1.tags, {"some": "stuff"})

        # Test power switch connections
        group_left = Group("left")
        group_left.entities.append("small-electric-pole", tile_position=(-2, 0))
        group_left.entities.append("power-switch")
        group_left.add_power_connection(0, 1, side=1)

        group_right = Group("right")
        group_right.entities.append("power-switch")
        group_right.entities.append("small-electric-pole", tile_position=(4, 0))
        group_right.add_power_connection(0, 1, side=2)

        blueprint = Blueprint()
        blueprint.entities.append(group_left)
        with self.assertRaises(ValueError):
            blueprint.entities.append(group_right, merge=True)

        # self.maxDiff = None
        # self.assertEqual(len(blueprint.entities), 2)
        # self.assertEqual(len(blueprint.entities[0].entities), 2)
        # self.assertEqual(len(blueprint.entities[1].entities), 1)
        # self.assertEqual(
        #     blueprint.to_dict()["blueprint"]["entities"],
        #     [
        #         {
        #             "entity_number": 1,
        #             "name": "small-electric-pole",
        #             "position": {"x": -1.5, "y": 0.5},
        #         },
        #         {
        #             "entity_number": 2,
        #             "name": "power-switch",
        #             "position": {"x": 1.0, "y": 1.0},
        #             "connections": {
        #                 "Cu0": [{"entity_id": 1, "wire_id": 0}],
        #                 "Cu1": [{"entity_id": 3, "wire_id": 0}]
        #             }
        #         },
        #         {
        #             "entity_number": 3,
        #             "name": "small-electric-pole",
        #             "position": {"x": 4.5, "y": 0.5},
        #         }
        #     ]
        # )

        # # Test self overlapping
        # group = Group()
        # group.entities.append("small-electric-pole", tile_position=(-2, 0))
        # group.entities.append("power-switch")
        # group.add_power_connection(0, 1, side=1)

        # blueprint = Blueprint()
        # blueprint.entities.append(group)
        # blueprint.entities.append(group, merge=True)

        # self.assertEqual(len(blueprint.entities), 2)
        # self.assertEqual(len(blueprint.entities[0].entities), 2)
        # self.assertEqual(len(blueprint.entities[1].entities), 0)
        # self.assertEqual(
        #     blueprint.to_dict()["blueprint"]["entities"],
        #     [
        #         {
        #             "entity_number": 1,
        #             "name": "small-electric-pole",
        #             "position": {"x": -1.5, "y": 0.5},
        #         },
        #         {
        #             "entity_number": 2,
        #             "name": "power-switch",
        #             "position": {"x": 1.0, "y": 1.0},
        #             "connections": {
        #                 "Cu0": [{"entity_id": 1, "wire_id": 0}],
        #             }
        #         },
        #     ]
        # )
