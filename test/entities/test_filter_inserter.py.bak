# test_filter_inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction, ReadMode
from draftsman.entity import FilterInserter, filter_inserters
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class FilterInserterTesting(unittest.TestCase):
    def test_constructor_init(self):
        # Valid
        inserter = FilterInserter(
            "filter-inserter",
            direction=Direction.EAST,
            tile_position=[1, 1],
            override_stack_size=1,
            filter_mode="blacklist",
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
            connections={"1": {"green": [{"entity_id": 2, "circuit_id": 1}]}},
            filters=["wooden-chest", "iron-chest", "steel-chest"],
        )
        self.assertEqual(
            inserter.to_dict(),
            {
                "name": "filter-inserter",
                "position": {"x": 1.5, "y": 1.5},
                "direction": 2,
                "override_stack_size": 1,
                "filter_mode": "blacklist",
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
                "connections": {"1": {"green": [{"entity_id": 2, "circuit_id": 1}]}},
                "filters": [
                    {"index": 1, "name": "wooden-chest"},
                    {"index": 2, "name": "iron-chest"},
                    {"index": 3, "name": "steel-chest"},
                ],
            },
        )

        inserter = FilterInserter(
            "filter-inserter",
            control_behavior={
                "stack_control_input_signal": {"name": "signal-A", "type": "virtual"}
            },
        )
        self.assertEqual(
            inserter.to_dict(),
            {
                "name": "filter-inserter",
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
            FilterInserter(position=[0, 0], direction=Direction.WEST, invalid_keyword=5)

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            FilterInserter("this is not a filter inserter")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            FilterInserter("filter-inserter", id=25)

        with self.assertRaises(TypeError):
            FilterInserter("filter-inserter", position=TypeError)

        with self.assertRaises(ValueError):
            FilterInserter("filter-inserter", direction="incorrect")

        with self.assertRaises(TypeError):
            FilterInserter("filter-inserter", override_stack_size="incorrect")

        with self.assertRaises(DataFormatError):
            FilterInserter(
                "filter-inserter", connections={"this is": ["very", "wrong"]}
            )

        with self.assertRaises(DataFormatError):
            FilterInserter(
                "filter-inserter",
                control_behavior={"this is": ["also", "very", "wrong"]},
            )

        with self.assertRaises(TypeError):
            FilterInserter(filter_mode=TypeError)
        with self.assertRaises(ValueError):
            FilterInserter("filter-inserter", filter_mode="wrong")

    def test_power_and_circuit_flags(self):
        for name in filter_inserters:
            inserter = FilterInserter(name)
            self.assertEqual(inserter.power_connectable, False)
            self.assertEqual(inserter.dual_power_connectable, False)
            self.assertEqual(inserter.circuit_connectable, True)
            self.assertEqual(inserter.dual_circuit_connectable, False)

    def test_set_filter_mode(self):
        inserter = FilterInserter()
        inserter.filter_mode = "blacklist"
        self.assertEqual(inserter.filter_mode, "blacklist")
        inserter.filter_mode = None
        self.assertEqual(inserter.filter_mode, None)
        with self.assertRaises(ValueError):
            inserter.filter_mode = "incorrect"

    def test_mergable_with(self):
        inserter1 = FilterInserter("filter-inserter")
        inserter2 = FilterInserter(
            "filter-inserter",
            filter_mode="whitelist",
            override_stack_size=1,
            filters=[{"name": "coal", "index": 1}],
        )
        self.assertTrue(inserter1.mergable_with(inserter1))

        self.assertTrue(inserter1.mergable_with(inserter2))
        self.assertTrue(inserter2.mergable_with(inserter1))

        inserter2.tile_position = (1, 1)
        self.assertFalse(inserter1.mergable_with(inserter2))

        inserter2.tile_position = (0, 0)
        inserter2.direction = Direction.EAST
        self.assertFalse(inserter1.mergable_with(inserter2))

        inserter2 = FilterInserter("stack-filter-inserter")
        self.assertFalse(inserter1.mergable_with(inserter2))

    def test_merge(self):
        inserter1 = FilterInserter("filter-inserter")
        inserter2 = FilterInserter(
            "filter-inserter",
            filter_mode="whitelist",
            override_stack_size=1,
            filters=[{"name": "coal", "index": 1}],
            tags={"some": "stuff"},
        )

        inserter1.merge(inserter2)
        del inserter2

        self.assertEqual(inserter1.filter_mode, "whitelist")
        self.assertEqual(inserter1.override_stack_size, 1)
        self.assertEqual(inserter1.filters, [{"name": "coal", "index": 1}])
        self.assertEqual(inserter1.tags, {"some": "stuff"})
