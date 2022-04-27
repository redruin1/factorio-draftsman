# test_inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction, ReadMode
from draftsman.entity import Inserter, inserters
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class InserterTesting(TestCase):
    def test_constructor_init(self):
        # Valid
        inserter = Inserter(
            "inserter",
            direction=Direction.EAST,
            tile_position=[1, 1],
            override_stack_size=1,
            control_behavior={
                "circuit_set_stack_size": True,
                "stack_control_input_signal": "signal-A",
                "circuit_enable_disable": True,
                "circuit_condition": {},
                "connect_to_logistic_network": True,
                "logistic_condition": {},
                "circuit_read_hand_contents": True,
                "circuit_hand_read_mode": ReadMode.PULSE,
            },
            connections={
                "1": {"green": [{"entity_id": "other_entity", "circuit_id": 1}]}
            },
        )
        self.assertEqual(
            inserter.to_dict(),
            {
                "name": "inserter",
                "position": {"x": 1.5, "y": 1.5},
                "direction": 2,
                "override_stack_size": 1,
                "control_behavior": {
                    "circuit_set_stack_size": True,
                    "stack_control_input_signal": {
                        "name": "signal-A",
                        "type": "virtual",
                    },
                    "circuit_enable_disable": True,
                    "circuit_condition": {},
                    "connect_to_logistic_network": True,
                    "logistic_condition": {},
                    "circuit_read_hand_contents": True,
                    "circuit_hand_read_mode": 0,
                },
                "connections": {
                    "1": {"green": [{"entity_id": "other_entity", "circuit_id": 1}]}
                },
            },
        )

        inserter = Inserter(
            "inserter",
            control_behavior={
                "stack_control_input_signal": {"name": "signal-A", "type": "virtual"}
            },
        )
        self.assertEqual(
            inserter.to_dict(),
            {
                "name": "inserter",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "stack_control_input_signal": {
                        "name": "signal-A",
                        "type": "virtual",
                    }
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Inserter(position=[0, 0], direction=Direction.WEST, invalid_keyword=5)

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            Inserter("this is not an inserter")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            Inserter("inserter", id=25)

        with self.assertRaises(TypeError):
            Inserter("inserter", position=TypeError)

        with self.assertRaises(ValueError):
            Inserter("inserter", direction="incorrect")

        with self.assertRaises(TypeError):
            Inserter("inserter", override_stack_size="incorrect")

        with self.assertRaises(DataFormatError):
            Inserter("inserter", connections={"this is": ["very", "wrong"]})

        with self.assertRaises(DataFormatError):
            Inserter(
                "inserter", control_behavior={"this is": ["also", "very", "wrong"]}
            )

    def test_power_and_circuit_flags(self):
        for name in inserters:
            inserter = Inserter(name)
            self.assertEqual(inserter.power_connectable, False)
            self.assertEqual(inserter.dual_power_connectable, False)
            self.assertEqual(inserter.circuit_connectable, True)
            self.assertEqual(inserter.dual_circuit_connectable, False)
