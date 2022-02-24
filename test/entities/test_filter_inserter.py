# test_filter_inserter.py

from draftsman.entity import FilterInserter, filter_inserters, Direction, ReadMode
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class FilterInserterTesting(TestCase):
    def test_default_constructor(self):
        inserter = FilterInserter()
        self.assertEqual(
            inserter.to_dict(),
            {
                "name": "filter-inserter",
                "position": {"x": 0.5, "y": 0.5},
            }
        )

    def test_constructor_init(self):
        # Valid
        inserter = FilterInserter(
            "filter-inserter", 
            direction = Direction.EAST,
            position = [1, 1],
            override_stack_size = 1,
            control_behavior = {
                "circuit_set_stack_size": True,
                "stack_control_input_signal": "signal-A",
                "circuit_enable_disable": True,
                "circuit_condition": {},
                "connect_to_logistic_network": True,
                "logistic_condition": {},
                "circuit_read_hand_contents": True,
                "circuit_hand_read_mode": ReadMode.PULSE
            },
            connections = {
                "1": {
                    "green": [
                        {"entity_id": "other_entity", "circuit_id": 1}
                    ]
                }
            },
            filters = ["wooden-chest", "iron-chest", "steel-chest"]
        )
        self.assertEqual(
            inserter.to_dict(),
            {
                "name": "filter-inserter",
                "position": {"x": 1.5, "y": 1.5},
                "direction": 2,
                "override_stack_size": 1,
                "control_behavior": {
                    "circuit_set_stack_size": True,
                    "stack_control_input_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "circuit_enable_disable": True,
                    "circuit_condition": {},
                    "connect_to_logistic_network": True,
                    "logistic_condition": {},
                    "circuit_read_hand_contents": True,
                    "circuit_hand_read_mode": 0
                },
                "connections": {
                        "1": {
                        "green": [
                            {"entity_id": "other_entity", "circuit_id": 1}
                        ]
                    }
                },
                "filters": [
                    {"index": 1, "name": "wooden-chest"},
                    {"index": 2, "name": "iron-chest"},
                    {"index": 3, "name": "steel-chest"},
                ]
            }
        )

        inserter = FilterInserter(
            "filter-inserter", control_behavior = {
                "stack_control_input_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )
        self.assertEqual(
            inserter.to_dict(),
            {
                "name": "filter-inserter",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "stack_control_input_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    }
                }
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            FilterInserter(
                position = [0, 0], direction = Direction.WEST, invalid_keyword = 5
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityID):
            FilterInserter("this is not a filter inserter")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(SchemaError):
            FilterInserter("filter-inserter", id = 25)

        with self.assertRaises(SchemaError):
            FilterInserter("filter-inserter", position = "invalid")
        
        with self.assertRaises(SchemaError):
            FilterInserter("filter-inserter", direction = "incorrect")

        with self.assertRaises(SchemaError):
            FilterInserter("filter-inserter", override_stack_size = "incorrect")

        with self.assertRaises(SchemaError):
            FilterInserter(
                "filter-inserter",
                connections = {
                    "this is": ["very", "wrong"]
                }
            )

        with self.assertRaises(SchemaError):
            FilterInserter(
                "filter-inserter",
                control_behavior = {
                    "this is": ["also", "very", "wrong"]
                }
            )

        with self.assertRaises(ValueError):
            FilterInserter(
                "filter-inserter",
                filter_mode = "wrong"
            )

    def test_power_and_circuit_flags(self):
        for name in filter_inserters:
            inserter = FilterInserter(name)
            self.assertEqual(inserter.power_connectable, False)
            self.assertEqual(inserter.dual_power_connectable, False)
            self.assertEqual(inserter.circuit_connectable, True)
            self.assertEqual(inserter.dual_circuit_connectable, False)
    
    def test_dimensions(self):
        for name in filter_inserters:
            inserter = FilterInserter(name)
            self.assertEqual(inserter.width, 1)
            self.assertEqual(inserter.height, 1)

    def test_set_filter_mode(self):
        inserter = FilterInserter()
        inserter.set_filter_mode("blacklist")
        self.assertEqual(inserter.filter_mode, "blacklist")
        inserter.set_filter_mode(None)
        self.assertEqual(inserter.filter_mode, None)

        with self.assertRaises(ValueError):
            inserter.set_filter_mode("incorrect")