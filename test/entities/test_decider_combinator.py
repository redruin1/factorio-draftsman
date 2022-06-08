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
    DraftsmanError,
)
from draftsman.warning import DraftsmanWarning
from draftsman.data import signals

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class DeciderCombinatorTesting(unittest.TestCase):
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

    def test_set_first_operand(self):
        combinator = DeciderCombinator("decider-combinator")
        self.assertEqual(combinator.first_operand, None)
        combinator.first_operand = "signal-A"
        self.assertEqual(
            combinator.first_operand, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"}
                }
            },
        )

        combinator.first_operand = {"name": "signal-B", "type": "virtual"}
        self.assertEqual(
            combinator.first_operand, {"name": "signal-B", "type": "virtual"}
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-B", "type": "virtual"}
                }
            },
        )

        combinator.first_operand = None
        self.assertEqual(combinator.first_operand, None)
        self.assertEqual(combinator.control_behavior, {"decider_conditions": {}})

        with self.assertRaises(TypeError):
            combinator.first_operand = TypeError
        with self.assertRaises(TypeError):
            combinator.first_operand = "incorrect"
        with self.assertRaises(TypeError):
            combinator.first_operand = 10

        combinator.remove_decider_conditions()
        combinator.output_signal = "signal-everything"
        combinator.first_operand = "signal-everything"
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-everything", "type": "virtual"},
                    "output_signal": {"name": "signal-everything", "type": "virtual"},
                }
            },
        )
        with self.assertWarns(DraftsmanWarning):
            combinator.first_operand = "signal-each"
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-each", "type": "virtual"}
                }
            },
        )

    def test_set_operation(self):
        combinator = DeciderCombinator("decider-combinator")
        self.assertEqual(combinator.operation, None)
        combinator.operation = "="
        self.assertEqual(combinator.operation, "=")
        self.assertEqual(
            combinator.control_behavior, {"decider_conditions": {"comparator": "="}}
        )

        combinator.operation = ">="
        self.assertEqual(combinator.operation, "≥")
        self.assertEqual(
            combinator.control_behavior, {"decider_conditions": {"comparator": "≥"}}
        )

        combinator.operation = None
        self.assertEqual(combinator.operation, None)
        self.assertEqual(combinator.control_behavior, {"decider_conditions": {}})

        with self.assertRaises(TypeError):
            combinator.operation = TypeError
        with self.assertRaises(TypeError):
            combinator.operation = "incorrect"

    def test_set_second_operand(self):
        combinator = DeciderCombinator("decider-combinator")
        self.assertEqual(combinator.second_operand, None)
        combinator.second_operand = "signal-A"
        self.assertEqual(
            combinator.second_operand, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "second_signal": {"name": "signal-A", "type": "virtual"}
                }
            },
        )

        combinator.second_operand = {"name": "signal-B", "type": "virtual"}
        self.assertEqual(
            combinator.second_operand, {"name": "signal-B", "type": "virtual"}
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "second_signal": {"name": "signal-B", "type": "virtual"}
                }
            },
        )

        combinator.second_operand = 100
        self.assertEqual(combinator.second_operand, 100)
        self.assertEqual(
            combinator.control_behavior, {"decider_conditions": {"constant": 100}}
        )

        combinator.first_operand = "signal-A"
        combinator.second_operand = None
        self.assertEqual(combinator.second_operand, None)
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"}
                }
            },
        )

        with self.assertRaises(TypeError):
            combinator.second_operand = TypeError
        with self.assertRaises(TypeError):
            combinator.second_operand = "incorrect"
        for pure_virtual_signal in signals.pure_virtual:
            with self.assertRaises(DraftsmanError):
                combinator.second_operand = pure_virtual_signal

    def test_set_output_signal(self):
        combinator = DeciderCombinator("decider-combinator")
        self.assertEqual(combinator.output_signal, None)
        combinator.output_signal = "signal-A"
        self.assertEqual(
            combinator.output_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "output_signal": {"name": "signal-A", "type": "virtual"}
                }
            },
        )

        combinator.output_signal = {"name": "signal-B", "type": "virtual"}
        self.assertEqual(
            combinator.output_signal, {"name": "signal-B", "type": "virtual"}
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "output_signal": {"name": "signal-B", "type": "virtual"}
                }
            },
        )

        combinator.output_signal = None
        self.assertEqual(combinator.output_signal, None)
        self.assertEqual(combinator.control_behavior, {"decider_conditions": {}})

        with self.assertRaises(TypeError):
            combinator.output_signal = TypeError
        with self.assertRaises(TypeError):
            combinator.output_signal = "incorrect"

        combinator.remove_decider_conditions()
        combinator.output_signal = "signal-everything"
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "output_signal": {"name": "signal-everything", "type": "virtual"}
                }
            },
        )
        with self.assertRaises(DraftsmanError):
            combinator.output_signal = "signal-anything"
        with self.assertRaises(DraftsmanError):
            combinator.output_signal = "signal-each"

        combinator.first_operand = "signal-everything"
        combinator.output_signal = "signal-everything"
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-everything", "type": "virtual"},
                    "output_signal": {"name": "signal-everything", "type": "virtual"},
                }
            },
        )
        with self.assertRaises(DraftsmanError):
            combinator.output_signal = "signal-anything"
        with self.assertRaises(DraftsmanError):
            combinator.output_signal = "signal-each"

        combinator.first_operand = "signal-anything"
        combinator.output_signal = "signal-everything"
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-anything", "type": "virtual"},
                    "output_signal": {"name": "signal-everything", "type": "virtual"},
                }
            },
        )
        combinator.output_signal = "signal-anything"
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-anything", "type": "virtual"},
                    "output_signal": {"name": "signal-anything", "type": "virtual"},
                }
            },
        )

        with self.assertRaises(DraftsmanError):
            combinator.output_signal = "signal-each"

        combinator.remove_decider_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-each", "type": "virtual"},
                    "output_signal": {"name": "signal-each", "type": "virtual"},
                }
            },
        )
        with self.assertRaises(DraftsmanError):
            combinator.output_signal = "signal-everything"
        with self.assertRaises(DraftsmanError):
            combinator.output_signal = "signal-anything"

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

        combinator.set_decider_conditions("signal-D", "<", 10, "signal-E")
        self.assertEqual(
            combinator.control_behavior,
            {
                "decider_conditions": {
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "<",
                    "constant": 10,
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                }
            },
        )

        combinator.set_decider_conditions(None, ">", 10)
        self.assertEqual(
            combinator.control_behavior,
            {"decider_conditions": {"constant": 10, "comparator": ">"}},
        )

        combinator.set_decider_conditions(None, None, None, None)
        self.assertEqual(combinator.control_behavior, {"decider_conditions": {}})

        combinator.set_decider_conditions()
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
