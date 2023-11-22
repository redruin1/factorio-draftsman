# test_arithmetic_combinator.py

from draftsman.constants import Direction, ValidationMode
from draftsman.entity import DeciderCombinator, decider_combinators, Container
from draftsman.error import (
    InvalidEntityError,
    DataFormatError,
    DraftsmanError,
)
from draftsman.signatures import SignalID
from draftsman.warning import (
    PureVirtualDisallowedWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
)

from draftsman.data import signals

from collections.abc import Hashable
from pydantic import ValidationError
import pytest


class TestDeciderCombinator:
    def test_constructor_init(self):
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
        assert combinator.to_dict() == {
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
        }

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
        assert combinator.to_dict() == {
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
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            DeciderCombinator(unused_keyword="whatever")
        with pytest.warns(UnknownKeywordWarning):
            DeciderCombinator(control_behavior={"unused_key": "something"})
        with pytest.warns(UnknownEntityWarning):
            DeciderCombinator("this is not an arithmetic combinator")

        # Errors
        with pytest.raises(DataFormatError):
            DeciderCombinator(control_behavior="incorrect")

    def test_power_and_circuit_flags(self):
        for name in decider_combinators:
            combinator = DeciderCombinator(name)
            assert combinator.power_connectable == False
            assert combinator.dual_power_connectable == False
            assert combinator.circuit_connectable == True
            assert combinator.dual_circuit_connectable == True

    def test_set_first_operand(self):
        combinator = DeciderCombinator("decider-combinator")
        assert combinator.first_operand == None
        combinator.first_operand = "signal-A"
        assert combinator.first_operand == SignalID(name="signal-A", type="virtual")

        combinator.first_operand = {"name": "signal-B", "type": "virtual"}
        assert combinator.first_operand == SignalID(name="signal-B", type="virtual")

        combinator.first_operand = None
        assert combinator.first_operand == None

        with pytest.raises(DataFormatError):
            combinator.first_operand = TypeError
        with pytest.raises(DataFormatError):
            combinator.first_operand = "incorrect"
        with pytest.raises(DataFormatError):
            combinator.first_operand = 10

        combinator.remove_decider_conditions()
        combinator.output_signal = "signal-everything"
        combinator.first_operand = "signal-everything"
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.first_operand = "signal-each"
        # We no longer set the output signal to none in the case of an invalid
        # configuration
        assert combinator.first_operand == SignalID(name="signal-each", type="virtual")
        assert combinator.output_signal == SignalID(
            name="signal-everything", type="virtual"
        )

        combinator.remove_decider_conditions()

        combinator.validate_assignment = "none"
        assert combinator.validate_assignment == ValidationMode.NONE

        combinator.first_operand = "incorrect"
        assert combinator.first_operand == "incorrect"
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 0.5, "y": 1.0},
            "control_behavior": {"decider_conditions": {"first_signal": "incorrect"}},
        }

    def test_set_operation(self):
        combinator = DeciderCombinator("decider-combinator")
        assert combinator.operation == "<"

        combinator.operation = "="
        assert combinator.operation == "="

        combinator.operation = ">="
        assert combinator.operation == "≥"

        combinator.operation = None
        assert combinator.operation == None

        with pytest.raises(DataFormatError):
            combinator.operation = TypeError
        with pytest.raises(DataFormatError):
            combinator.operation = "incorrect"

        combinator.remove_decider_conditions()

        combinator.validate_assignment = "none"
        assert combinator.validate_assignment == ValidationMode.NONE

        combinator.operation = "incorrect"
        assert combinator.operation == "incorrect"
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 0.5, "y": 1.0},
            "control_behavior": {"decider_conditions": {"comparator": "incorrect"}},
        }

    def test_set_second_operand(self):
        combinator = DeciderCombinator("decider-combinator")
        assert combinator.second_operand == 0

        combinator.second_operand = "signal-A"
        print(combinator.control_behavior)
        assert combinator.second_operand == SignalID(name="signal-A", type="virtual")

        combinator.second_operand = {"name": "signal-B", "type": "virtual"}
        assert combinator.second_operand == SignalID(name="signal-B", type="virtual")

        combinator.second_operand = 100
        assert combinator.second_operand == 100

        combinator.first_operand = "signal-A"
        combinator.second_operand = None
        assert combinator.second_operand == None

        with pytest.raises(DataFormatError):
            combinator.second_operand = TypeError
        with pytest.raises(DataFormatError):
            combinator.second_operand = "incorrect"
        for pure_virtual_signal in signals.pure_virtual:
            with pytest.warns(PureVirtualDisallowedWarning):
                combinator.second_operand = pure_virtual_signal

        combinator.control_behavior.decider_conditions = None
        assert combinator.control_behavior.decider_conditions == None
        assert combinator.second_operand == None

        combinator.remove_decider_conditions()

        combinator.validate_assignment = "none"
        assert combinator.validate_assignment == ValidationMode.NONE

        combinator.second_operand = 100.0
        assert combinator.second_operand == 100.0
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 0.5, "y": 1.0},
            "control_behavior": {"decider_conditions": {"constant": 100.0}},
        }

        combinator.second_operand = "incorrect"
        assert combinator.second_operand == "incorrect"
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 0.5, "y": 1.0},
            "control_behavior": {"decider_conditions": {"second_signal": "incorrect"}},
        }

    def test_set_output_signal(self):
        combinator = DeciderCombinator("decider-combinator")
        assert combinator.output_signal == None
        combinator.output_signal = "signal-A"
        assert combinator.output_signal == SignalID(name="signal-A", type="virtual")

        combinator.output_signal = {"name": "signal-B", "type": "virtual"}
        assert combinator.output_signal == SignalID(name="signal-B", type="virtual")

        combinator.output_signal = None
        assert combinator.output_signal == None

        with pytest.raises(DataFormatError):
            combinator.output_signal = TypeError
        with pytest.raises(DataFormatError):
            combinator.output_signal = "incorrect"

        combinator.remove_decider_conditions()
        combinator.output_signal = "signal-everything"
        assert combinator.output_signal == SignalID(
            name="signal-everything", type="virtual"
        )

        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.output_signal = "signal-anything"
        assert combinator.output_signal == SignalID(
            name="signal-anything", type="virtual"
        )
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.output_signal = "signal-each"
        assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

        combinator.remove_decider_conditions()
        combinator.first_operand = "signal-everything"
        combinator.output_signal = "signal-everything"
        assert combinator.first_operand == SignalID(
            name="signal-everything", type="virtual"
        )
        assert combinator.output_signal == SignalID(
            name="signal-everything", type="virtual"
        )

        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.output_signal = "signal-anything"
        assert combinator.output_signal == SignalID(
            name="signal-anything", type="virtual"
        )
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.output_signal = "signal-each"
        assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

        combinator.remove_decider_conditions()
        combinator.first_operand = "signal-anything"
        combinator.output_signal = "signal-everything"
        assert combinator.first_operand == SignalID(
            name="signal-anything", type="virtual"
        )
        assert combinator.output_signal == SignalID(
            name="signal-everything", type="virtual"
        )

        combinator.output_signal = "signal-anything"
        assert combinator.first_operand == SignalID(
            name="signal-anything", type="virtual"
        )
        assert combinator.output_signal == SignalID(
            name="signal-anything", type="virtual"
        )

        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.output_signal = "signal-each"
        assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

        combinator.remove_decider_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.first_operand == SignalID(name="signal-each", type="virtual")
        assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.output_signal = "signal-everything"
        assert combinator.output_signal == SignalID(
            name="signal-everything", type="virtual"
        )
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.output_signal = "signal-anything"
        assert combinator.output_signal == SignalID(
            name="signal-anything", type="virtual"
        )

        combinator.remove_decider_conditions()

        combinator.validate_assignment = "none"
        assert combinator.validate_assignment == ValidationMode.NONE

        combinator.output_signal = "incorrect"
        assert combinator.output_signal == "incorrect"
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 0.5, "y": 1.0},
            "control_behavior": {"decider_conditions": {"output_signal": "incorrect"}},
        }

    def test_set_copy_count_from_input(self):
        combinator = DeciderCombinator()
        assert combinator.copy_count_from_input == True

        combinator.copy_count_from_input = False
        assert combinator.copy_count_from_input == False

        combinator.copy_count_from_input = None
        assert combinator.copy_count_from_input == None

        # Error
        with pytest.raises(DataFormatError):
            combinator.copy_count_from_input = "incorrect"

        combinator.validate_assignment = "none"
        assert combinator.validate_assignment == ValidationMode.NONE

        combinator.copy_count_from_input = "incorrect"
        assert combinator.copy_count_from_input == "incorrect"
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 0.5, "y": 1.0},
            "control_behavior": {
                "decider_conditions": {"copy_count_from_input": "incorrect"}
            },
        }

    def test_set_decider_conditions(self):
        combinator = DeciderCombinator()
        combinator.set_decider_conditions("signal-A", ">", "iron-ore")
        assert combinator.control_behavior == DeciderCombinator.Format.ControlBehavior(
            **{
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": ">",
                    "second_signal": {"name": "iron-ore", "type": "item"},
                }
            }
        )
        combinator.set_decider_conditions("signal-A", "=", "copper-ore", "signal-B")
        assert combinator.control_behavior == DeciderCombinator.Format.ControlBehavior(
            **{
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "second_signal": {"name": "copper-ore", "type": "item"},
                    "output_signal": {"name": "signal-B", "type": "virtual"},
                }
            }
        )

        combinator.set_decider_conditions("signal-D", "<", 10, "signal-E")
        assert combinator.control_behavior == DeciderCombinator.Format.ControlBehavior(
            **{
                "decider_conditions": {
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "<",
                    "constant": 10,
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                }
            }
        )

        combinator.set_decider_conditions(None, ">", 10)
        assert combinator.control_behavior == DeciderCombinator.Format.ControlBehavior(
            **{"decider_conditions": {"constant": 10, "comparator": ">"}}
        )

        # combinator.set_decider_conditions(None, None, None, None)
        # assert combinator.control_behavior == DeciderCombinator.Format.ControlBehavior(**{"decider_conditions": {}})

        combinator.set_decider_conditions()
        assert combinator.control_behavior == DeciderCombinator.Format.ControlBehavior(
            **{"decider_conditions": {"comparator": "<", "constant": 0}}
        )

        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions(TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("incorrect")
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "incorrect", "signal-D")
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "incorrect")
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "signal-D", TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "signal-D", "incorrect")

        # TODO:
        assert combinator.control_behavior == DeciderCombinator.Format.ControlBehavior(
            **{"decider_conditions": {"comparator": "<", "constant": 0}}
        )

        # Test Remove conditions
        combinator.control_behavior = None
        assert combinator.control_behavior == None

    def test_mergable_with(self):
        comb1 = DeciderCombinator("decider-combinator", direction=Direction.SOUTH)
        comb2 = DeciderCombinator(
            "decider-combinator",
            direction=Direction.SOUTH,
            control_behavior={
                "decider_conditions": {
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "<",
                    "constant": 10,
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                    "copy_count_from_input": False,
                }
            },
            tags={"some": "stuff"},
        )

        assert comb1.mergable_with(comb2)
        assert comb2.mergable_with(comb1)

        comb2.first_operand = "signal-A"
        comb2.operation = ">="
        assert comb1.mergable_with(comb2)

        comb2.direction = Direction.NORTH
        assert not comb1.mergable_with(comb2)

    def test_merge(self):
        comb1 = DeciderCombinator(
            "decider-combinator",
            direction=Direction.SOUTH,
            control_behavior={
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "second_signal": {"name": "copper-ore", "type": "item"},
                    "output_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
            tags={"original": "tags"},
        )
        comb2 = DeciderCombinator(
            "decider-combinator",
            direction=Direction.SOUTH,
            control_behavior={
                "decider_conditions": {
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "<",
                    "constant": 10,
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                    "copy_count_from_input": False,
                }
            },
        )

        comb1.merge(comb2)
        del comb2

        assert comb1.control_behavior == DeciderCombinator.Format.ControlBehavior(
            **{
                "decider_conditions": {
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "<",
                    "constant": 10,
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                    "copy_count_from_input": False,
                }
            }
        )
        assert comb1.tags == {}  # Overwritten by comb2

    def test_eq(self):
        decider1 = DeciderCombinator("decider-combinator")
        decider2 = DeciderCombinator("decider-combinator")

        assert decider1 == decider2

        decider1.tags = {"some": "stuff"}

        assert decider1 != decider2

        container = Container()

        assert decider1 != container
        assert decider2 != container

        # hashable
        assert isinstance(decider1, Hashable)
