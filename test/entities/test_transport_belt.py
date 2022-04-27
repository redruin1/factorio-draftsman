# test_transport_belt.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction, ReadMode
from draftsman.entity import TransportBelt, transport_belts
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class TransportBeltTesting(TestCase):
    def test_constructor_init(self):
        # Valid
        fast_belt = TransportBelt(
            "fast-transport-belt",
            tile_position=[0, 0],
            direction=Direction.EAST,
            connections={"1": {"green": [{"entity_id": 1}]}},
            control_behavior={
                "circuit_enable_disable": True,
                "circuit_condition": {
                    "first_signal": "signal-blue",
                    "comparator": "=",
                    "second_signal": "signal-blue",
                },
                "connect_to_logistic_network": True,
                "logistic_condition": {
                    "first_signal": "fast-underground-belt",
                    "comparator": ">=",
                    "constant": 0,
                },
                "circuit_read_hand_contents": False,
                "circuit_contents_read_mode": ReadMode.HOLD,
            },
        )
        self.maxDiff = None
        self.assertEqual(
            fast_belt.to_dict(),
            {
                "name": "fast-transport-belt",
                "direction": 2,
                "position": {"x": 0.5, "y": 0.5},
                "connections": {"1": {"green": [{"entity_id": 1}]}},
                "control_behavior": {
                    "circuit_enable_disable": True,
                    "circuit_condition": {
                        "first_signal": {"name": "signal-blue", "type": "virtual"},
                        "comparator": "=",
                        "second_signal": {"name": "signal-blue", "type": "virtual"},
                    },
                    "connect_to_logistic_network": True,
                    "logistic_condition": {
                        "first_signal": {
                            "name": "fast-underground-belt",
                            "type": "item",
                        },
                        "comparator": "≥",
                        "constant": 0,
                    },
                    "circuit_read_hand_contents": False,
                    "circuit_contents_read_mode": ReadMode.HOLD,
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            temp = TransportBelt("fast-transport-belt", invalid_param=100)

        # Errors
        # Raises InvalidEntityID when not in transport_belts
        with self.assertRaises(InvalidEntityError):
            TransportBelt("this is not a storage tank")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            TransportBelt("transport-belt", id=25)

        with self.assertRaises(TypeError):
            TransportBelt("transport-belt", position=TypeError)

        with self.assertRaises(ValueError):
            TransportBelt("transport-belt", direction="incorrect")

        with self.assertRaises(DataFormatError):
            TransportBelt("transport-belt", connections={"this is": ["very", "wrong"]})

        with self.assertRaises(DataFormatError):
            TransportBelt(
                "transport-belt",
                control_behavior={"this is": ["also", "very", "wrong"]},
            )

    def test_power_and_circuit_flags(self):
        for transport_belt in transport_belts:
            belt = TransportBelt(transport_belt)
            self.assertEqual(belt.power_connectable, False)
            self.assertEqual(belt.dual_power_connectable, False)
            self.assertEqual(belt.circuit_connectable, True)
            self.assertEqual(belt.dual_circuit_connectable, False)
