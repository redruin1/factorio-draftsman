# test_arithmetic_combinator.py

from draftsman.constants import Direction
from draftsman.entity import ArithmeticCombinator, arithmetic_combinators
from draftsman.errors import InvalidEntityID, InvalidSignalID, InvalidArithmeticOperation

from schema import SchemaError

from unittest import TestCase

class ArithmeticCombinatorTesting(TestCase):
    def test_default_constructor(self):
        combinator = ArithmeticCombinator()
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "arithmetic-combinator",
                "position": {"x": 0.5, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        combinator = ArithmeticCombinator(
            "arithmetic-combinator",
            position = [3, 3],
            direction = Direction.EAST,
            control_behavior = {
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "operation": "+",
                    "second_constant": 10
                }
            }
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
                        "second_constant": 10
                    }
                }
            }
        )

        combinator = ArithmeticCombinator(
            "arithmetic-combinator",
            position = [3, 3],
            direction = Direction.EAST,
            control_behavior = {
                "arithmetic_conditions": {
                    "first_signal": "signal-A",
                    "operation": "*",
                    "second_signal": "signal-B"
                }
            }
        )
        self.assertEqual(
            combinator.to_dict(),
            {
                "name": "arithmetic-combinator",
                "position": {"x": 4.0, "y": 3.5},
                "direction": 2,
                "control_behavior": {
                    "arithmetic_conditions": {
                        "first_signal": {
                            "name": "signal-A",
                            "type": "virtual"
                        },
                        "operation": "*",
                        "second_signal": {
                            "name": "signal-B",
                            "type": "virtual"
                        }
                    }
                }
            }
        )

        combinator = ArithmeticCombinator(
            "arithmetic-combinator",
            position = [3, 3],
            direction = Direction.EAST,
            control_behavior = {
                "arithmetic_conditions": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "operation": "*",
                    "second_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    }
                }
            }
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
                        "first_signal": {
                            "name": "signal-A",
                            "type": "virtual"
                        },
                        "operation": "*",
                        "second_signal": {
                            "name": "signal-B",
                            "type": "virtual"
                        }
                    }
                }
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            ArithmeticCombinator(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            ArithmeticCombinator("this is not an arithmetic combinator")

    def test_flags(self):
        for name in arithmetic_combinators:
            combinator = ArithmeticCombinator(name)
            self.assertEqual(combinator.power_connectable, False)
            self.assertEqual(combinator.dual_power_connectable, False)
            self.assertEqual(combinator.circuit_connectable, True)
            self.assertEqual(combinator.dual_circuit_connectable, True)

    def test_dimensions(self):
        combinator = ArithmeticCombinator()
        self.assertEqual(combinator.tile_width, 1)
        self.assertEqual(combinator.tile_height, 2)

    def test_set_arithmetic_conditions(self):
        combinator = ArithmeticCombinator()
        combinator.set_arithmetic_conditions("signal-A", "+", "iron-ore")
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "operation": "+",
                    "second_signal": {
                        "name": "iron-ore",
                        "type": "item"
                    }
                }
            }
        )
        combinator.set_arithmetic_conditions("signal-A", "/", "copper-ore", "signal-B")
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "operation": "/",
                    "second_signal": {
                        "name": "copper-ore",
                        "type": "item"
                    },
                    "output_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    }
                }
            }
        )
        combinator.set_arithmetic_conditions(10, "and", 100, "signal-C")
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "operation": "AND",
                    "second_constant": 100,
                    "output_signal": {
                        "name": "signal-C",
                        "type": "virtual"
                    }
                }
            }
        )

        combinator.set_arithmetic_conditions(None, None, None, None)
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {}
            }
        )

        combinator.set_arithmetic_conditions(None)
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "operation": "*",
                    "second_constant": 0
                }
            }
        )

        with self.assertRaises(SchemaError):
            combinator.set_arithmetic_conditions(TypeError)
        with self.assertRaises(SchemaError):
            combinator.set_arithmetic_conditions("incorrect")
        with self.assertRaises(SchemaError):
            combinator.set_arithmetic_conditions("signal-A", "incorrect", "signal-D")
        with self.assertRaises(SchemaError):
            combinator.set_arithmetic_conditions("signal-A", "+", TypeError)
        with self.assertRaises(SchemaError):
            combinator.set_arithmetic_conditions("signal-A", "+", "incorrect")
        with self.assertRaises(SchemaError):
            combinator.set_arithmetic_conditions("signal-A", "+", "signal-D", TypeError)
        with self.assertRaises(SchemaError):
            combinator.set_arithmetic_conditions("signal-A", "+", "signal-D", "incorrect")

        # TODO:
        self.assertEqual(
            combinator.control_behavior,
            {
                "arithmetic_conditions": {
                    "operation": "*",
                    "second_constant": 0
                }
            }
        )

        # Test Remove conditions
        combinator.remove_arithmetic_conditions()
        self.assertEqual(combinator.control_behavior, {})