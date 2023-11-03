# test_arithmetic_combinator.py

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
from draftsman.signatures import SignalID
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning, PureVirtualDisallowedWarning, SignalConfigurationWarning, UnknownSignalWarning

from collections.abc import Hashable
import sys
import pytest


class TestArithmeticCombinator:
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
                    "operation": "/",
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
                    "operation": "/",
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
                    "operation": ">>",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
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
                    "operation": ">>",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            ArithmeticCombinator(unused_keyword="whatever")
        with pytest.warns(UnknownKeywordWarning):
            ArithmeticCombinator(control_behavior={"unused_key": "something"})
        with pytest.warns(UnknownKeywordWarning):
            ArithmeticCombinator(control_behavior={"arithmetic_conditions": {"unused_key": "something"}})
        with pytest.warns(UnknownEntityWarning):
            ArithmeticCombinator("this is not an arithmetic combinator")

        # Errors        
        with pytest.raises(DataFormatError):
            ArithmeticCombinator(control_behavior="incorrect")

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
        
        combinator.second_operand = 200
        assert combinator.first_operand == 100
        assert combinator.second_operand == 200
        
        combinator.first_operand = "signal-A"
        assert combinator.first_operand == SignalID(**{"name": "signal-A", "type": "virtual"})
        assert combinator.second_operand == 200

        combinator.first_operand = None
        assert combinator.first_operand == None

        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.first_operand = "signal-anything"
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.first_operand = "signal-everything"

        with pytest.raises(DataFormatError):
            combinator.first_operand = TypeError

        # Ensure that signal-each cannot be applied to each operand simultaneously
        combinator.remove_arithmetic_conditions()
        combinator.second_operand = "signal-each"
        with pytest.warns(SignalConfigurationWarning):
            combinator.first_operand = "signal-each"

        # Test remove output signal-each when current is unset from signal-each
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.first_operand == SignalID(name="signal-each", type="virtual")
        assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

        # Setting to the same signal should issue no warnings
        combinator.first_operand = "signal-each"
        assert combinator.first_operand == SignalID(name="signal-each", type="virtual")

        # Setting to non special should issue a warning, but not remove the output
        with pytest.warns(SignalConfigurationWarning):
            combinator.first_operand = "signal-A"
        assert combinator.first_operand == SignalID(name="signal-A", type="virtual")
        assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

    def test_set_operation(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.operation == "*"

        combinator.operation = "xor"
        assert combinator.operation == "XOR"

        combinator.operation = ">>"
        assert combinator.operation == ">>"

        combinator.operation = None
        assert combinator.operation == None

        with pytest.raises(DataFormatError):
            combinator.operation = TypeError
        with pytest.raises(DataFormatError):
            combinator.operation = "incorrect"

    def test_set_second_operand(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.second_operand == 0
        
        combinator.second_operand = 100
        assert combinator.second_operand == 100
        assert combinator.control_behavior.arithmetic_conditions.second_constant == 100

        combinator.first_operand = 200
        assert combinator.second_operand == 100
        assert combinator.first_operand == 200
        assert combinator.control_behavior.arithmetic_conditions.first_constant == 200

        combinator.second_operand = "signal-A"
        assert combinator.second_operand == SignalID(**{"name": "signal-A", "type": "virtual"})
        assert combinator.control_behavior.arithmetic_conditions.second_signal == SignalID(**{"name": "signal-A", "type": "virtual"})
        assert combinator.control_behavior.arithmetic_conditions.second_constant == None

        combinator.second_operand = None
        assert combinator.second_operand == None
        assert combinator.control_behavior.arithmetic_conditions.second_signal == None
        assert combinator.control_behavior.arithmetic_conditions.second_constant == None

        # Warn against forbidden virtual signals
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.second_operand = "signal-anything"
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.second_operand = "signal-everything"

        with pytest.raises(DataFormatError):
            combinator.second_operand = TypeError

        # Ensure that signal-each cannot be applied to each operand simultaneously
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        with pytest.warns(SignalConfigurationWarning):
            combinator.second_operand = "signal-each"

        combinator.remove_arithmetic_conditions()
        combinator.second_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.second_operand == SignalID(name="signal-each", type="virtual")
        assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

        # Setting to the same signal should issue no warnings
        combinator.second_operand = "signal-each"
        assert combinator.second_operand == SignalID(name="signal-each", type="virtual")

        # Setting to non special should issue a warning, but not remove the output
        with pytest.warns(SignalConfigurationWarning):
            combinator.second_operand = "signal-A"
        assert combinator.second_operand == SignalID(name="signal-A", type="virtual")
        assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

    def test_set_output_signal(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.output_signal == None

        combinator.output_signal = "signal-A"
        assert combinator.output_signal == SignalID(**{"name": "signal-A", "type": "virtual"})

        combinator.output_signal = {"name": "signal-B", "type": "virtual"}
        assert combinator.output_signal == SignalID(**{"name": "signal-B", "type": "virtual"})

        combinator.output_signal = None
        assert combinator.output_signal == None

        # Warnings
        # only signal-each is allowed in arithmetic combinators
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.output_signal = "signal-everything"
        # Warn if signal each is output, but neither of inputs
        with pytest.warns(SignalConfigurationWarning):
            combinator.output_signal = "signal-each"
        # All info is known, but Draftsman doesn't recognize
        with pytest.warns(UnknownSignalWarning):
            combinator.output_signal = {"name": "unknown", "type": "virtual"}

        # Errors
        with pytest.raises(DataFormatError):
            combinator.output_signal = TypeError
        with pytest.raises(DataFormatError):
            combinator.output_signal = "incorrect"

        # Test valid signal-each
        combinator.remove_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"

        # Warn if both inputs are signal-each
        with pytest.warns(SignalConfigurationWarning):
            combinator.second_operand = "signal-each"

    def test_set_arithmetic_conditions(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        combinator.set_arithmetic_conditions("signal-A", "+", "iron-ore")
        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "+",
                "second_signal": {"name": "iron-ore", "type": "item"},
            }
        })
        combinator.set_arithmetic_conditions("signal-A", "/", "copper-ore", "signal-B")
        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "/",
                "second_signal": {"name": "copper-ore", "type": "item"},
                "output_signal": {"name": "signal-B", "type": "virtual"},
            }
        })
        combinator.set_arithmetic_conditions(10, "and", 100, "signal-C")
        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {
                "first_constant": 10,
                "operation": "AND",
                "second_constant": 100,
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        })

        combinator.set_arithmetic_conditions(10, "or", "signal-D", "signal-E")
        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {
                "first_constant": 10,
                "operation": "OR",
                "second_signal": {"name": "signal-D", "type": "virtual"},
                "output_signal": {"name": "signal-E", "type": "virtual"},
            }
        })

        combinator.set_arithmetic_conditions(10, "or", None)
        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {"first_constant": 10, "operation": "OR"}
        })

        combinator.set_arithmetic_conditions(None, None, None, None)
        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{"arithmetic_conditions": {}})

        combinator.set_arithmetic_conditions(None)
        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {"operation": "*", "second_constant": 0}
        })

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

        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {"operation": "*", "second_constant": 0}
        })

        # Test Remove conditions
        combinator.remove_arithmetic_conditions()
        assert combinator.control_behavior == ArithmeticCombinator.Format.ControlBehavior()

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
        assert combinatorA.control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "+",
                "second_signal": {"name": "signal-B", "type": "virtual"},
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        })

        # Test blueprint merging
        blueprint = Blueprint()
        blueprint.entities.append("arithmetic-combinator")

        entity_to_merge = ArithmeticCombinator("arithmetic-combinator")
        entity_to_merge.set_arithmetic_conditions(
            "signal-A", "+", "signal-B", "signal-C"
        )

        blueprint.entities.append(entity_to_merge, merge=True)

        assert len(blueprint.entities) == 1
        assert blueprint.entities[0].control_behavior == ArithmeticCombinator.Format.ControlBehavior(**{
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "+",
                "second_signal": {"name": "signal-B", "type": "virtual"},
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        })

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
