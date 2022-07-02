# test_arithmetic_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.blueprint import Blueprint
from draftsman.constants import Direction
from draftsman.entity import ArithmeticCombinator, arithmetic_combinators, Container
from draftsman.error import (
    InvalidEntityError,
    InvalidSignalError,
    DataFormatError,
    DraftsmanError,
)
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class ArithmeticCombinatorTesting(unittest.TestCase):
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

    def test_set_first_operand(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        self.assertEqual(combinator.first_operand, None)
        combinator.first_operand = 100
        self.assertEqual(combinator.first_operand, 100)
        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"first_constant": 100}},
        )
        combinator.second_operand = 200
        self.assertEqual(combinator.first_operand, 100)
        self.assertEqual(combinator.second_operand, 200)
        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"first_constant": 100, "second_constant": 200}},
        )
        combinator.first_operand = "signal-A"
        self.assertEqual(
            combinator.first_operand, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(combinator.second_operand, 200)
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "second_constant": 200,
                }
            },
        )

        combinator.first_operand = None
        self.assertEqual(combinator.first_operand, None)
        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"second_constant": 200}},
        )

        with self.assertRaises(TypeError):
            combinator.first_operand = TypeError
        with self.assertRaises(DraftsmanError):
            combinator.first_operand = "signal-anything"
        with self.assertRaises(DraftsmanError):
            combinator.first_operand = "signal-everything"

        # Ensure that signal-each cannot be applied to each operand simultaneously
        combinator.remove_arithmetic_conditions()
        combinator.second_operand = "signal-each"
        with self.assertRaises(DraftsmanError):
            combinator.first_operand = "signal-each"

        # Test remove output signal-each when current is unset from signal-each
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-each", "type": "virtual"},
                    "output_signal": {"name": "signal-each", "type": "virtual"},
                }
            },
        )

        # Setting to the same signal should remain the same
        combinator.first_operand = "signal-each"
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-each", "type": "virtual"},
                    "output_signal": {"name": "signal-each", "type": "virtual"},
                }
            },
        )

        # Setting to non special should remove output_signal
        with self.assertWarns(DraftsmanWarning):
            combinator.first_operand = "signal-A"
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                }
            },
        )

    def test_set_operation(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        self.assertEqual(combinator.operation, None)
        combinator.operation = "xor"
        self.assertEqual(combinator.operation, "XOR")
        self.assertEqual(
            combinator.control_behavior, {"arithmetic_conditions": {"operation": "XOR"}}
        )

        combinator.operation = ">>"
        self.assertEqual(combinator.operation, ">>")
        self.assertEqual(
            combinator.control_behavior, {"arithmetic_conditions": {"operation": ">>"}}
        )

        combinator.operation = None
        self.assertEqual(combinator.operation, None)
        self.assertEqual(combinator.control_behavior, {"arithmetic_conditions": {}})

        with self.assertRaises(TypeError):
            combinator.operation = TypeError
        with self.assertRaises(TypeError):
            combinator.operation = "incorrect"

    def test_set_second_operand(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        self.assertEqual(combinator.second_operand, None)
        combinator.second_operand = 100
        self.assertEqual(combinator.second_operand, 100)
        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"second_constant": 100}},
        )
        combinator.first_operand = 200
        self.assertEqual(combinator.second_operand, 100)
        self.assertEqual(combinator.first_operand, 200)
        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"first_constant": 200, "second_constant": 100}},
        )
        combinator.second_operand = "signal-A"
        self.assertEqual(
            combinator.second_operand, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(combinator.first_operand, 200)
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_constant": 200,
                    "second_signal": {"name": "signal-A", "type": "virtual"},
                }
            },
        )

        combinator.second_operand = None
        self.assertEqual(combinator.second_operand, None)
        self.assertEqual(
            combinator.control_behavior,
            {"arithmetic_conditions": {"first_constant": 200}},
        )

        with self.assertRaises(TypeError):
            combinator.second_operand = TypeError
        with self.assertRaises(DraftsmanError):
            combinator.second_operand = "signal-anything"
        with self.assertRaises(DraftsmanError):
            combinator.second_operand = "signal-everything"

        # Ensure that signal-each cannot be applied to each operand simultaneously
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        with self.assertRaises(DraftsmanError):
            combinator.second_operand = "signal-each"

        # Test remove output signal-each when current is unset from signal-each
        combinator.remove_arithmetic_conditions()
        combinator.second_operand = "signal-each"
        combinator.output_signal = "signal-each"
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "second_signal": {"name": "signal-each", "type": "virtual"},
                    "output_signal": {"name": "signal-each", "type": "virtual"},
                }
            },
        )

        # Setting to the same signal should remain the same
        combinator.second_operand = "signal-each"
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "second_signal": {"name": "signal-each", "type": "virtual"},
                    "output_signal": {"name": "signal-each", "type": "virtual"},
                }
            },
        )

        # Setting to non special should remove output_signal
        with self.assertWarns(DraftsmanWarning):
            combinator.second_operand = "signal-A"
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "second_signal": {"name": "signal-A", "type": "virtual"},
                }
            },
        )

    def test_set_output_signal(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        self.assertEqual(combinator.output_signal, None)
        combinator.output_signal = "signal-A"
        self.assertEqual(
            combinator.output_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
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
                "arithmetic_conditions": {
                    "output_signal": {"name": "signal-B", "type": "virtual"}
                }
            },
        )

        combinator.output_signal = None
        self.assertEqual(combinator.output_signal, None)
        self.assertEqual(combinator.control_behavior, {"arithmetic_conditions": {}})

        with self.assertRaises(TypeError):
            combinator.output_signal = TypeError
        with self.assertRaises(TypeError):
            combinator.output_signal = "incorrect"
        with self.assertRaises(InvalidSignalError):
            combinator.output_signal = "signal-everything"
        # Raise error if signal-each is not first or second operand
        with self.assertRaises(DraftsmanError):
            combinator.output_signal = "signal-each"

        # Test valid signal-each
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-each", "type": "virtual"},
                    "output_signal": {"name": "signal-each", "type": "virtual"},
                }
            },
        )

    def test_set_arithmetic_conditions(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
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

    def test_mergable(self):
        combinatorA = ArithmeticCombinator("arithmetic-combinator")
        combinatorB = ArithmeticCombinator("arithmetic-combinator")

        # Compatible
        self.assertEqual(combinatorA.mergable_with(combinatorB), True)

        combinatorB.set_arithmetic_conditions("signal-A", "+", "signal-B", "signal-C")
        self.assertEqual(combinatorA.mergable_with(combinatorB), True)

        # Incompatible
        self.assertEqual(combinatorA.mergable_with(Container()), False)

        combinatorB.tile_position = (10, 0)
        self.assertEqual(combinatorA.mergable_with(combinatorB), False)
        combinatorB.tile_position = (0, 0)

        combinatorB.id = "something"
        self.assertEqual(combinatorA.mergable_with(combinatorB), False)
        combinatorB.id = None

        combinatorB.direction = Direction.SOUTH
        self.assertEqual(combinatorA.mergable_with(combinatorB), False)
        combinatorB.direction = Direction.NORTH

    def test_merge(self):
        combinatorA = ArithmeticCombinator("arithmetic-combinator")
        combinatorB = ArithmeticCombinator("arithmetic-combinator")
        combinatorB.set_arithmetic_conditions("signal-A", "+", "signal-B", "signal-C")

        combinatorA.merge(combinatorB)
        self.assertEqual(
            combinatorA.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "operation": "+",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                    "output_signal": {"name": "signal-C", "type": "virtual"}
                }
            }
        )

        # Test blueprint merging
        blueprint = Blueprint()
        blueprint.entities.append("arithmetic-combinator")

        entity_to_merge = ArithmeticCombinator("arithmetic-combinator")
        entity_to_merge.set_arithmetic_conditions("signal-A", "+", "signal-B", "signal-C")

        blueprint.entities.append(entity_to_merge, merge=True)

        self.assertEqual(len(blueprint.entities), 1)
        self.assertEqual(
            blueprint.entities[0].control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "operation": "+",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                    "output_signal": {"name": "signal-C", "type": "virtual"}
                }
            }
        )
