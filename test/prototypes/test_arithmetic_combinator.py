# test_arithmetic_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.entity import ArithmeticCombinator, arithmetic_combinators, Container
from draftsman.error import (
    InvalidEntityError,
    InvalidSignalError,
    DataFormatError,
    DraftsmanError,
)
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

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
        assert combinator.to_dict() == {
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
        }

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
        assert combinator.to_dict() == {
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
        }

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
        assert combinator.to_dict() == {
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
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            ArithmeticCombinator(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            ArithmeticCombinator("this is not an arithmetic combinator")
        with pytest.raises(DataFormatError):
            ArithmeticCombinator(control_behavior={"unused_key": "something"})

    def test_flags(self):
        for name in arithmetic_combinators:
            combinator = ArithmeticCombinator(name)
            assert combinator.power_connectable == False
            assert combinator.dual_power_connectable == False
            assert combinator.circuit_connectable == True
            assert combinator.dual_circuit_connectable == True

    def test_set_first_operand(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.first_operand == None
        combinator.first_operand = 100
        assert combinator.first_operand == 100
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"first_constant": 100}
        }
        combinator.second_operand = 200
        assert combinator.first_operand == 100
        assert combinator.second_operand == 200
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"first_constant": 100, "second_constant": 200}
        }
        combinator.first_operand = "signal-A"
        assert combinator.first_operand == {"name": "signal-A", "type": "virtual"}
        assert combinator.second_operand == 200
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "second_constant": 200,
            }
        }

        combinator.first_operand = None
        assert combinator.first_operand == None
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"second_constant": 200}
        }

        with pytest.raises(TypeError):
            combinator.first_operand = TypeError
        with pytest.raises(DraftsmanError):
            combinator.first_operand = "signal-anything"
        with pytest.raises(DraftsmanError):
            combinator.first_operand = "signal-everything"

        # Ensure that signal-each cannot be applied to each operand simultaneously
        combinator.remove_arithmetic_conditions()
        combinator.second_operand = "signal-each"
        with pytest.raises(DraftsmanError):
            combinator.first_operand = "signal-each"

        # Test remove output signal-each when current is unset from signal-each
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-each", "type": "virtual"},
                "output_signal": {"name": "signal-each", "type": "virtual"},
            }
        }

        # Setting to the same signal should remain the same
        combinator.first_operand = "signal-each"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-each", "type": "virtual"},
                "output_signal": {"name": "signal-each", "type": "virtual"},
            }
        }

        # Setting to non special should remove output_signal
        with pytest.warns(DraftsmanWarning):
            combinator.first_operand = "signal-A"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
            }
        }

    def test_set_operation(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.operation == None
        combinator.operation = "xor"
        assert combinator.operation == "XOR"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"operation": "XOR"}
        }

        combinator.operation = ">>"
        assert combinator.operation == ">>"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"operation": ">>"}
        }

        combinator.operation = None
        assert combinator.operation == None
        assert combinator.control_behavior == {"arithmetic_conditions": {}}

        with pytest.raises(TypeError):
            combinator.operation = TypeError
        with pytest.raises(TypeError):
            combinator.operation = "incorrect"

    def test_set_second_operand(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.second_operand == None
        combinator.second_operand = 100
        assert combinator.second_operand == 100
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"second_constant": 100}
        }
        combinator.first_operand = 200
        assert combinator.second_operand == 100
        assert combinator.first_operand == 200
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"first_constant": 200, "second_constant": 100}
        }
        combinator.second_operand = "signal-A"
        assert combinator.second_operand == {"name": "signal-A", "type": "virtual"}
        assert combinator.first_operand == 200
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_constant": 200,
                "second_signal": {"name": "signal-A", "type": "virtual"},
            }
        }

        combinator.second_operand = None
        assert combinator.second_operand == None
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"first_constant": 200}
        }

        with pytest.raises(TypeError):
            combinator.second_operand = TypeError
        with pytest.raises(DraftsmanError):
            combinator.second_operand = "signal-anything"
        with pytest.raises(DraftsmanError):
            combinator.second_operand = "signal-everything"

        # Ensure that signal-each cannot be applied to each operand simultaneously
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        with pytest.raises(DraftsmanError):
            combinator.second_operand = "signal-each"

        # Test remove output signal-each when current is unset from signal-each
        combinator.remove_arithmetic_conditions()
        combinator.second_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "second_signal": {"name": "signal-each", "type": "virtual"},
                "output_signal": {"name": "signal-each", "type": "virtual"},
            }
        }

        # Setting to the same signal should remain the same
        combinator.second_operand = "signal-each"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "second_signal": {"name": "signal-each", "type": "virtual"},
                "output_signal": {"name": "signal-each", "type": "virtual"},
            }
        }

        # Setting to non special should remove output_signal
        with pytest.warns(DraftsmanWarning):
            combinator.second_operand = "signal-A"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "second_signal": {"name": "signal-A", "type": "virtual"},
            }
        }

    def test_set_output_signal(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.output_signal == None
        combinator.output_signal = "signal-A"
        assert combinator.output_signal == {"name": "signal-A", "type": "virtual"}
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "output_signal": {"name": "signal-A", "type": "virtual"}
            }
        }

        combinator.output_signal = {"name": "signal-B", "type": "virtual"}
        assert combinator.output_signal == {"name": "signal-B", "type": "virtual"}
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "output_signal": {"name": "signal-B", "type": "virtual"}
            }
        }

        combinator.output_signal = None
        assert combinator.output_signal == None
        assert combinator.control_behavior == {"arithmetic_conditions": {}}

        with pytest.raises(TypeError):
            combinator.output_signal = TypeError
        with pytest.raises(TypeError):
            combinator.output_signal = "incorrect"
        with pytest.raises(InvalidSignalError):
            combinator.output_signal = "signal-everything"
        # Raise error if signal-each is not first or second operand
        with pytest.raises(DraftsmanError):
            combinator.output_signal = "signal-each"

        # Test valid signal-each
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-each", "type": "virtual"},
                "output_signal": {"name": "signal-each", "type": "virtual"},
            }
        }

    def test_set_arithmetic_conditions(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        combinator.set_arithmetic_conditions("signal-A", "+", "iron-ore")
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "+",
                "second_signal": {"name": "iron-ore", "type": "item"},
            }
        }
        combinator.set_arithmetic_conditions("signal-A", "/", "copper-ore", "signal-B")
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "/",
                "second_signal": {"name": "copper-ore", "type": "item"},
                "output_signal": {"name": "signal-B", "type": "virtual"},
            }
        }
        combinator.set_arithmetic_conditions(10, "and", 100, "signal-C")
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_constant": 10,
                "operation": "AND",
                "second_constant": 100,
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        }

        combinator.set_arithmetic_conditions(10, "or", "signal-D", "signal-E")
        assert combinator.control_behavior == {
            "arithmetic_conditions": {
                "first_constant": 10,
                "operation": "OR",
                "second_signal": {"name": "signal-D", "type": "virtual"},
                "output_signal": {"name": "signal-E", "type": "virtual"},
            }
        }

        combinator.set_arithmetic_conditions(10, "or", None)
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"first_constant": 10, "operation": "OR"}
        }

        combinator.set_arithmetic_conditions(None, None, None, None)
        assert combinator.control_behavior == {"arithmetic_conditions": {}}

        combinator.set_arithmetic_conditions(None)
        assert combinator.control_behavior == {
            "arithmetic_conditions": {"operation": "*", "second_constant": 0}
        }

        # TODO: change these from SchemaErrors
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions(TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions("incorrect")
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions("signal-A", "incorrect", "signal-D")
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions("signal-A", "+", TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions("signal-A", "+", "incorrect")
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions("signal-A", "+", "signal-D", TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions(
                "signal-A", "+", "signal-D", "incorrect"
            )

        assert combinator.control_behavior == {
            "arithmetic_conditions": {"operation": "*", "second_constant": 0}
        }

        # Test Remove conditions
        combinator.remove_arithmetic_conditions()
        assert combinator.control_behavior == {}

    def test_mergable(self):
        combinatorA = ArithmeticCombinator("arithmetic-combinator")
        combinatorB = ArithmeticCombinator("arithmetic-combinator")

        # Compatible
        assert combinatorA.mergable_with(combinatorB) == True

        combinatorB.set_arithmetic_conditions("signal-A", "+", "signal-B", "signal-C")
        assert combinatorA.mergable_with(combinatorB) == True

        # Incompatible
        assert combinatorA.mergable_with(Container()) == False

        combinatorB.tile_position = (10, 0)
        assert combinatorA.mergable_with(combinatorB) == False
        combinatorB.tile_position = (0, 0)

        combinatorB.id = "something"
        assert combinatorA.mergable_with(combinatorB) == False
        combinatorB.id = None

        combinatorB.direction = Direction.SOUTH
        assert combinatorA.mergable_with(combinatorB) == False
        combinatorB.direction = Direction.NORTH

    def test_merge(self):
        combinatorA = ArithmeticCombinator("arithmetic-combinator")
        combinatorB = ArithmeticCombinator("arithmetic-combinator")
        combinatorB.set_arithmetic_conditions("signal-A", "+", "signal-B", "signal-C")

        combinatorA.merge(combinatorB)
        assert combinatorA.control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "+",
                "second_signal": {"name": "signal-B", "type": "virtual"},
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        }

        # Test blueprint merging
        blueprint = Blueprint()
        blueprint.entities.append("arithmetic-combinator")

        entity_to_merge = ArithmeticCombinator("arithmetic-combinator")
        entity_to_merge.set_arithmetic_conditions(
            "signal-A", "+", "signal-B", "signal-C"
        )

        blueprint.entities.append(entity_to_merge, merge=True)

        assert len(blueprint.entities) == 1
        assert blueprint.entities[0].control_behavior == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "+",
                "second_signal": {"name": "signal-B", "type": "virtual"},
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        }

        # Test dual-circuit-connections as well as self-reference
        group = Group()
        group.entities.append("arithmetic-combinator")
        group.add_circuit_connection("green", 0, 0, 1, 2)

        blueprint = Blueprint()
        blueprint.entities.append("arithmetic-combinator")
        blueprint.entities.append(group, merge=True)

        assert len(blueprint.entities) == 2
        assert len(blueprint.entities[1].entities) == 0
        assert blueprint.to_dict()["blueprint"]["entities"] == [
            {
                "entity_number": 1,
                "name": "arithmetic-combinator",
                "position": {"x": 0.5, "y": 1.0},
                "connections": {
                    "1": {"green": [{"entity_id": 1, "circuit_id": 2}]},
                    "2": {"green": [{"entity_id": 1, "circuit_id": 1}]},
                },
            }
        ]

    def test_eq(self):
        combinatorA = ArithmeticCombinator("arithmetic-combinator")
        combinatorB = ArithmeticCombinator("arithmetic-combinator")

        assert combinatorA == combinatorB

        combinatorA.set_arithmetic_conditions(1, "*", 1, "signal-check")

        assert combinatorA != combinatorB

        container = Container("wooden-chest")

        assert combinatorA != container
        assert combinatorB != container

        # hashable
        assert isinstance(combinatorA, Hashable)
