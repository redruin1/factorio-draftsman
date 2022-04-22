# test_arithmetic_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import ArithmeticCombinator, arithmetic_combinators
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


class ArithmeticCombinatorTesting(TestCase):
    def test_constructor_init(self):
        combinator = ArithmeticCombinator(
            "arithmetic-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "operation": "+",
                    "second_constant": 10,
                }
            },
        )
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "arithmetic-combinator",
                "position": {"x": 4.0, "y": 3.5},
                "direction": 2,
                "control_behavior": {
                    "arithmetic_conditions": {
                        "first_constant": 10,
                        "operation": "+",
                        "second_constant": 10,
                    }
                },
            },
        )

        combinator = ArithmeticCombinator(
            "arithmetic-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "arithmetic_conditions": {
                    "first_signal": "signal-A",
                    "operation": "*",
                    "second_signal": "signal-B",
                }
            },
        )
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "arithmetic-combinator",
                "position": {"x": 4.0, "y": 3.5},
                "direction": 2,
                "control_behavior": {
                    "arithmetic_conditions": {
                        "first_signal": {"name": "signal-A", "type": "virtual"},
                        "operation": "*",
                        "second_signal": {"name": "signal-B", "type": "virtual"},
                    }
                },
            },
        )

        combinator = ArithmeticCombinator(
            "arithmetic-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "operation": "*",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )
        self.maxDiff = None
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "arithmetic-combinator",
                "position": {"x": 4.0, "y": 3.5},
                "direction": 2,
                "control_behavior": {
                    "arithmetic_conditions": {
                        "first_signal": {"name": "signal-A", "type": "virtual"},
                        "operation": "*",
                        "second_signal": {"name": "signal-B", "type": "virtual"},
                    }
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            ArithmeticCombinator(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            ArithmeticCombinator("this is not an arithmetic combinator")

    def test_flags(self):
        for name in arithmetic_combinators:
            combinator = ArithmeticCombinator(name)
            self.assertEqual(combinator.power_connectable, False)
            self.assertEqual(combinator.dual_power_connectable, False)
            self.assertEqual(combinator.circuit_connectable, True)
            self.assertEqual(combinator.dual_circuit_connectable, True)

    # def test_set_first_operand(self):
    #     combinator = ArithmeticCombinator()
    #     self.assertEqual(combinator.first_operand, None)
    #     combinator.first_operand = 100
    #     self.assertEqual(combinator.first_operand, 100)
    #     self.assertEqual(
    #         combinator.control_behavior,
    #         {
    #             "arithmetic_conditions": {
    #                 "constant": 100
    #             }
    #         }
    #     )
    #     combinator.second_operand = 200
    #     self.assertEqual(combinator.first_operand, 100)
    #     self.assertEqual(combinator.second_operand, 200)
    #     self.assertEqual(
    #         combinator.control_behavior,
    #         {
    #             "arithmetic_conditions": {
    #                 "first_constant": 100,
    #                 "second_constant": 200
    #             }
    #         }
    #     )
    #     combinator.first_operand = "signal-A"
    #     self.assertEqual(combinator.first_operand, {"name": "signal-A", "type": "virtual"})
    #     self.assertEqual(combinator.second_operand, 200)
    #     self.assertEqual(
    #         combinator.control_behavior,
    #         {
    #             "arithmetic_conditions": {
    #                 "first_signal": {"name": "signal-A", "type": "virtual"},
    #                 "constant": 200
    #             }
    #         }
    #     )

    #     combinator.first_operand = None
    #     self.assertEqual(combinator.first_operand, None)
    #     self.assertEqual(
    #         combinator.control_behavior,
    #         {
    #             "arithmetic_conditions": {
    #                 "constant": 200
    #             }
    #         }
    #     )

    #     with self.assertRaises(TypeError):
    #         combinator.first_operand = TypeError

    # def test_set_operation(self):
    #     combinator = ArithmeticCombinator()
    #     combinator.operation = "xor"
    #     self.assertEqual(combinator.operation, "XOR")
    #     self.assertEqual(
    #         combinator.control_behavior,
    #         {
    #             "arithmetic_conditions": {
    #                 "operation": "XOR"
    #             }
    #         }
    #     )

    def test_set_arithmetic_conditions(self):
        combinator = ArithmeticCombinator()
        combinator.set_arithmetic_conditions("signal-A", "+", "iron-ore")
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "operation": "+",
                    "second_signal": {"name": "iron-ore", "type": "item"},
                }
            },
        )
        combinator.set_arithmetic_conditions("signal-A", "/", "copper-ore", "signal-B")
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "operation": "/",
                    "second_signal": {"name": "copper-ore", "type": "item"},
                    "output_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )
        combinator.set_arithmetic_conditions(10, "and", 100, "signal-C")
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "operation": "AND",
                    "second_constant": 100,
                    "output_signal": {"name": "signal-C", "type": "virtual"},
                }
            },
        )

        combinator.set_arithmetic_conditions(10, "or", "signal-D", "signal-E")
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "operation": "OR",
                    "second_signal": {"name": "signal-D", "type": "virtual"},
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                }
            },
        )

        combinator.set_arithmetic_conditions(10, "or", None)
        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"first_constant": 10, "operation": "OR"}},
        )

        combinator.set_arithmetic_conditions(None, None, None, None)
        self.assertEqual(combinator.control_behavior, {"arithmetic_conditions": {}})

        combinator.set_arithmetic_conditions(None)
        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"operation": "*", "second_constant": 0}},
        )

        # TODO: change these from SchemaErrors
        with self.assertRaises(DataFormatError):
            combinator.set_arithmetic_conditions(TypeError)
        with self.assertRaises(DataFormatError):
            combinator.set_arithmetic_conditions("incorrect")
        with self.assertRaises(DataFormatError):
            combinator.set_arithmetic_conditions("signal-A", "incorrect", "signal-D")
        with self.assertRaises(DataFormatError):
            combinator.set_arithmetic_conditions("signal-A", "+", TypeError)
        with self.assertRaises(DataFormatError):
            combinator.set_arithmetic_conditions("signal-A", "+", "incorrect")
        with self.assertRaises(DataFormatError):
            combinator.set_arithmetic_conditions("signal-A", "+", "signal-D", TypeError)
        with self.assertRaises(DataFormatError):
            combinator.set_arithmetic_conditions(
                "signal-A", "+", "signal-D", "incorrect"
            )

        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"operation": "*", "second_constant": 0}},
        )

        # Test Remove conditions
        combinator.remove_arithmetic_conditions()
        self.assertEqual(combinator.control_behavior, {})
