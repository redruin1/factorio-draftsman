# test_arithmetic_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import DeciderCombinator, decider_combinators
from draftsman.error import (
    InvalidEntityError,
    InvalidSignalError,
    InvalidOperationError,
    DataFormatError,
)
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class DeciderCombinatorTesting(TestCase):
    def test_constructor_init(self):
        combinator = DeciderCombinator(
            "decider-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "decider_conditions": {"first_constant": 10, "second_constant": 10}
            },
        )
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "decider-combinator",
                "position": {"x": 4.0, "y": 3.5},
                "direction": 2,
                "control_behavior": {
                    "decider_conditions": {"first_constant": 10, "second_constant": 10}
                },
            },
        )

        combinator = DeciderCombinator(
            "decider-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "decider_conditions": {
                    "first_signal": "signal-A",
                    "comparator": ">=",
                    "second_signal": "signal-B",
                }
            },
        )
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "decider-combinator",
                "position": {"x": 4.0, "y": 3.5},
                "direction": Direction.EAST,
                "control_behavior": {
                    "decider_conditions": {
                        "first_signal": {"name": "signal-A", "type": "virtual"},
                        "comparator": "≥",
                        "second_signal": {"name": "signal-B", "type": "virtual"},
                    }
                },
            },
        )

        combinator = DeciderCombinator(
            "decider-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "<=",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )
        self.maxDiff = None
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "decider-combinator",
                "position": {"x": 4.0, "y": 3.5},
                "direction": 2,
                "control_behavior": {
                    "decider_conditions": {
                        "first_signal": {"name": "signal-A", "type": "virtual"},
                        "comparator": "≤",
                        "second_signal": {"name": "signal-B", "type": "virtual"},
                    }
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            DeciderCombinator(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            DeciderCombinator("this is not an arithmetic combinator")

    def test_flags(self):
        for name in decider_combinators:
            combinator = DeciderCombinator(name)
            self.assertEqual(combinator.power_connectable, False)
            self.assertEqual(combinator.dual_power_connectable, False)
            self.assertEqual(combinator.circuit_connectable, True)
            self.assertEqual(combinator.dual_circuit_connectable, True)

    def test_set_decider_conditions(self):
        combinator = DeciderCombinator()
        combinator.set_decider_conditions("signal-A", ">", "iron-ore")
        self.maxDiff = None
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": ">",
                    "second_signal": {"name": "iron-ore", "type": "item"},
                }
            },
        )
        combinator.set_decider_conditions("signal-A", "=", "copper-ore", "signal-B")
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "second_signal": {"name": "copper-ore", "type": "item"},
                    "output_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )
        combinator.set_decider_conditions(10, "<=", 100, "signal-C")
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_constant": 10,
                    "comparator": "≤",
                    "second_constant": 100,
                    "output_signal": {"name": "signal-C", "type": "virtual"},
                }
            },
        )

        combinator.set_decider_conditions(10, ">", "signal-D", "signal-E")
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "constant": 10,
                    "comparator": ">",
                    "second_signal": {"name": "signal-D", "type": "virtual"},
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                }
            },
        )

        combinator.set_decider_conditions(10, ">", None)
        self.assertEqual(
            combinator.control_behavior,
            {"decider_conditions": {"constant": 10, "comparator": ">"}},
        )

        combinator.set_decider_conditions(None, None, None, None)
        self.assertEqual(combinator.control_behavior, {"decider_conditions": {}})

        combinator.set_decider_conditions(None)
        self.assertEqual(
            combinator.control_behavior,
            {"decider_conditions": {"comparator": "<", "constant": 0}},
        )

        with self.assertRaises(DataFormatError):
            combinator.set_decider_conditions(TypeError)
        with self.assertRaises(DataFormatError):
            combinator.set_decider_conditions("incorrect")
        with self.assertRaises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "incorrect", "signal-D")
        with self.assertRaises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", TypeError)
        with self.assertRaises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "incorrect")
        with self.assertRaises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "signal-D", TypeError)
        with self.assertRaises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "signal-D", "incorrect")

        # TODO:
        self.assertEqual(
            combinator.control_behavior,
            {"decider_conditions": {"comparator": "<", "constant": 0}},
        )

        # Test Remove conditions
        combinator.remove_decider_conditions()
        self.assertEqual(combinator.control_behavior, {})

        # Test set_copy_count
        self.assertEqual(combinator.copy_count_from_input, None)
        combinator.copy_count_from_input = True
        self.assertEqual(combinator.copy_count_from_input, True)
        self.assertEqual(
            combinator.control_behavior,
            {"decider_conditions": {"copy_count_from_input": True}},
        )
        combinator.copy_count_from_input = False
        self.assertEqual(
            combinator.control_behavior,
            {"decider_conditions": {"copy_count_from_input": False}},
        )
        combinator.copy_count_from_input = None
        self.assertEqual(  # maybe should be == {}?
            combinator.control_behavior, {"decider_conditions": {}}
        )

        # Error
        with self.assertRaises(TypeError):
            combinator.copy_count_from_input = "incorrect"
