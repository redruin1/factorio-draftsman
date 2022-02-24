# test_transport_belt.py

from draftsman.entity import (
    TransportBelt, transport_belts, Direction, ModeOfOperation
)
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class TransportBeltTesting(TestCase):
    def test_default_constructor(self):
        belt = TransportBelt()
        self.assertEqual(
            belt.to_dict(),
            {
                "name": transport_belts[0],
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        # Valid
        fast_belt = TransportBelt("fast-transport-belt", 
            position = [0, 0], direction = Direction.EAST,
            connections = {
                "1": {
                    "green": [
                        {"entity_id": 1}
                    ]
                }
            },
            control_behavior = {
                "circuit_enable_disable": True,
                "circuit_condition": {
                    "first_signal": "signal-blue",
                    "comparator": "=",
                    "second_signal": "signal-blue"
                },
                "connect_to_logistic_network": True,
                "logistic_condition": {
                    "first_signal": "fast-underground-belt",
                    "comparator": ">=",
                    "constant": 0
                },
                "circuit_read_hand_contents": False,
                "circuit_contents_read_mode": ModeOfOperation.NONE
            }
        )
        self.assertEqual(
            fast_belt.to_dict(),
            {
                "name": "fast-transport-belt",
                "direction": 2,
                "position": {"x": 0.5, "y": 0.5},
                "connections": {
                    "1": {
                        "green": [
                            {"entity_id": 1}
                        ]
                    }
                },
                "control_behavior": {
                    "circuit_enable_disable": True,
                    "circuit_condition": {
                        "first_signal": {
                            "name": "signal-blue",
                            "type": "virtual"
                        },
                        "comparator": "=",
                        "second_signal": {
                            "name": "signal-blue",
                            "type": "virtual"
                        }
                    },
                    "connect_to_logistic_network": True,
                    "logistic_condition": {
                        "first_signal": {
                            "name": "fast-underground-belt",
                            "type": "item"
                        },
                        "comparator": "≥",
                        "constant": 0
                    },
                    "circuit_read_hand_contents": False,
                    "circuit_contents_read_mode": ModeOfOperation.NONE
                }
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            temp = TransportBelt("fast-transport-belt", invalid_param = 100)

        # Errors
        # Raises InvalidEntityID when not in transport_belts
        with self.assertRaises(InvalidEntityID):
            TransportBelt("this is not a storage tank")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(SchemaError):
            TransportBelt("transport-belt", id = 25)

        with self.assertRaises(SchemaError):
            TransportBelt("transport-belt", position = "invalid")
        
        with self.assertRaises(SchemaError):
            TransportBelt("transport-belt", direction = "incorrect")

        with self.assertRaises(SchemaError):
            TransportBelt(
                "transport-belt",
                connections = {
                    "this is": ["very", "wrong"]
                }
            )

        with self.assertRaises(SchemaError):
            TransportBelt(
                "transport-belt",
                control_behavior = {
                    "this is": ["also", "very", "wrong"]
                }
            )

    def test_power_and_circuit_flags(self):
        for transport_belt in transport_belts:
            belt = TransportBelt(transport_belt)
            self.assertEqual(belt.power_connectable, False)
            self.assertEqual(belt.dual_power_connectable, False)
            self.assertEqual(belt.circuit_connectable, True)
            self.assertEqual(belt.dual_circuit_connectable, False)

    def test_dimensions(self):
        for transport_belt in transport_belts:
            belt = TransportBelt(transport_belt)
            self.assertEqual(belt.width, 1)
            self.assertEqual(belt.height, 1)