# test_arithmetic_combinator.py

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction, ValidationMode
from draftsman.entity import ArithmeticCombinator, arithmetic_combinators, Container
from draftsman.error import DataFormatError, IncompleteSignalError
from draftsman.signatures import SignalID
import draftsman.validators
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    PureVirtualDisallowedWarning,
    SignalConfigurationWarning,
    UnknownSignalWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_arithmetic_combinator():
    if len(arithmetic_combinators) == 0:
        return None
    return ArithmeticCombinator(
        "arithmetic-combinator",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        player_description="test",
        first_operand="signal-A",
        first_operand_wires={"red"},
        operation="XOR",
        second_operand="signal-B",
        second_operand_wires={"green"},
        output_signal="signal-C",
        tags={"blah": "blah"},
    )


class TestArithmeticCombinator:
    def test_constructor_init(self):
        combinator = ArithmeticCombinator(
            "arithmetic-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            first_operand=10,
            operation="+",
            second_operand=10,
        )
        assert combinator.to_dict() == {
            "name": "arithmetic-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "direction": 4,
            "control_behavior": {
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "operation": "+",
                    "second_constant": 10,
                }
            },
        }
        assert combinator.to_dict(exclude_none=False) == {
            "name": "arithmetic-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "direction": 4,
            "control_behavior": {
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "operation": "+",
                    "second_constant": 10,
                }
            },
        }
        assert combinator.to_dict(exclude_defaults=False) == {
            "name": "arithmetic-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "quality": "normal",
            "mirror": False,
            "direction": 4,
            "player_description": "",
            "control_behavior": {
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "first_signal_networks": {"green": True, "red": True},
                    "operation": "+",
                    "second_constant": 10,
                    "second_signal_networks": {"green": True, "red": True},
                }
            },
            "tags": {},
        }
        assert combinator.to_dict(exclude_none=False, exclude_defaults=False) == {
            "name": "arithmetic-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "quality": "normal",
            "mirror": False,
            "direction": 4,
            "player_description": "",
            "control_behavior": {
                "arithmetic_conditions": {
                    "first_constant": 10,
                    "first_signal_networks": {"green": True, "red": True},
                    "first_signal": None,
                    "operation": "+",
                    "second_constant": 10,
                    "second_signal_networks": {"green": True, "red": True},
                    "second_signal": None,
                    "output_signal": None,
                }
            },
            "tags": {},
        }

        combinator = ArithmeticCombinator(
            "arithmetic-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            first_operand="signal-A",
            operation="/",
            second_operand="signal-B",
        )
        assert combinator.to_dict() == {
            "name": "arithmetic-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "direction": Direction.EAST,
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
            first_operand={"name": "signal-A", "type": "virtual"},
            operation="xor",
            second_operand={"name": "signal-B", "type": "virtual"},
        )
        assert combinator.to_dict() == {
            "name": "arithmetic-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "direction": Direction.EAST,
            "control_behavior": {
                "arithmetic_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "operation": "XOR",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            ArithmeticCombinator(
                "this is not an arithmetic combinator"
            ).validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            ArithmeticCombinator(tags="incorrect").validate().reissue_all()

    def test_1_0_serialization(self):
        combinator = ArithmeticCombinator(player_description="Wanna see a magic trick?")
        assert combinator.to_dict(version=(2, 0)) == {
            "name": "arithmetic-combinator",
            "position": {"x": 0.5, "y": 1.0},
            "player_description": "Wanna see a magic trick?",
        }
        assert combinator.to_dict(version=(1, 0)) == {
            "name": "arithmetic-combinator",
            "position": {"x": 0.5, "y": 1.0},
        }

    def test_power_and_circuit_flags(self):
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
        assert combinator.first_operand == SignalID(
            **{"name": "signal-A", "type": "virtual"}
        )
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
        # TODO: only on 1.0 is this true
        combinator.second_operand = "signal-each"
        # with pytest.warns(SignalConfigurationWarning): # 1.0 test
        #     combinator.first_operand = "signal-each"

        # Test remove output signal-each when current is unset from signal-each
        combinator.set_arithmetic_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.first_operand == SignalID(
            name="signal-each", type="virtual"
        )
        assert combinator.output_signal == SignalID(
            name="signal-each", type="virtual"
        )

        # Setting to the same signal should issue no warnings
        combinator.first_operand = "signal-each"
        assert combinator.first_operand == SignalID(
            name="signal-each", type="virtual"
        )

        # Setting to non special should issue a warning, but not remove the output
        # TODO: reimplement
        # with pytest.warns(SignalConfigurationWarning):
        #     combinator.first_operand = "signal-A"
        # assert combinator.first_operand == SignalID(name="signal-A", type="virtual")
        # assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

    def test_set_operation(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.operation == "*"

        combinator.operation = "xor"
        assert combinator.operation == "XOR"

        combinator.operation = ">>"
        assert combinator.operation == ">>"

        with pytest.raises(DataFormatError):
            combinator.operation = TypeError
        with pytest.raises(DataFormatError):
            combinator.operation = "incorrect"

    def test_set_second_operand(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.second_operand == 0

        combinator.second_operand = 100
        assert combinator.second_operand == 100

        combinator.first_operand = 200
        assert combinator.second_operand == 100
        assert combinator.first_operand == 200

        combinator.second_operand = "signal-A"
        assert combinator.second_operand == SignalID(
            **{"name": "signal-A", "type": "virtual"}
        )

        combinator.second_operand = None
        assert combinator.second_operand == None

        # Warn against forbidden virtual signals
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.second_operand = "signal-anything"
        with pytest.warns(PureVirtualDisallowedWarning):
            combinator.second_operand = "signal-everything"

        with pytest.raises(DataFormatError):
            combinator.second_operand = TypeError

        # Ensure that signal-each cannot be applied to each operand simultaneously
        # TODO: only on 1.0 is this true
        combinator.first_operand = "signal-each"
        # with pytest.warns(SignalConfigurationWarning): # 1.0 test
        #     combinator.second_operand = "signal-each"

        combinator.set_arithmetic_conditions()
        combinator.second_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.second_operand == SignalID(
            name="signal-each", type="virtual"
        )
        assert combinator.output_signal == SignalID(
            name="signal-each", type="virtual"
        )

        # Setting to the same signal should issue no warnings
        combinator.second_operand = "signal-each"
        assert combinator.second_operand == SignalID(
            name="signal-each", type="virtual"
        )

        # Setting to non special should issue a warning, but not remove the output
        # TODO: reimplement
        # with pytest.warns(SignalConfigurationWarning):
        #     combinator.second_operand = "signal-A"
        # assert combinator.second_operand == SignalID(name="signal-A", type="virtual")
        # assert combinator.output_signal == SignalID(name="signal-each", type="virtual")

    def test_set_output_signal(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.output_signal == None

        combinator.output_signal = "signal-A"
        assert combinator.output_signal == SignalID(
            **{"name": "signal-A", "type": "virtual"}
        )

        combinator.output_signal = {"name": "signal-B", "type": "virtual"}
        assert combinator.output_signal == SignalID(
            **{"name": "signal-B", "type": "virtual"}
        )

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

        # No warnings
        with draftsman.validators.set_mode(ValidationMode.MINIMUM):
            combinator.output_signal = "signal-everything"
            assert combinator.output_signal == SignalID(
                name="signal-everything", type="virtual"
            )
            combinator.output_signal = "signal-each"
            assert combinator.output_signal == SignalID(
                name="signal-each", type="virtual"
            )

        # Errors
        with pytest.raises(DataFormatError):
            combinator.output_signal = TypeError
        with pytest.raises(IncompleteSignalError):
            combinator.output_signal = "incorrect"

        # Test valid signal-each
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"

        # Warn if both inputs are signal-each
        # with pytest.warns(SignalConfigurationWarning): # 1.0 test
        #     combinator.second_operand = "signal-each"

    def test_set_arithmetic_conditions(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        combinator.set_arithmetic_conditions(
            "signal-A",
            {"red", "green"},
            "+",
            "iron-ore",
            {"red", "green"},
        )
        assert combinator.to_dict()["control_behavior"] == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "+",
                "second_signal": {"name": "iron-ore", "type": "item"},
            }
        }

        combinator.set_arithmetic_conditions(
            "signal-A",
            {"red", "green"},
            "/",
            "copper-ore",
            {"red", "green"},
            "signal-B",
        )
        assert combinator.to_dict()["control_behavior"] == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "operation": "/",
                "second_signal": {"name": "copper-ore", "type": "item"},
                "output_signal": {"name": "signal-B", "type": "virtual"},
            }
        }

        combinator.set_arithmetic_conditions(
            first_operand=10,
            operation="and",
            second_operand=100,
            output_signal="signal-C",
        )
        assert combinator.to_dict()["control_behavior"] == {
            "arithmetic_conditions": {
                "first_constant": 10,
                "operation": "AND",
                "second_constant": 100,
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        }

        combinator.set_arithmetic_conditions(
            first_operand=10,
            operation="or",
            second_operand="signal-D",
            output_signal="signal-E",
        )
        assert combinator.to_dict()["control_behavior"] == {
            "arithmetic_conditions": {
                "first_constant": 10,
                "operation": "OR",
                "second_signal": {"name": "signal-D", "type": "virtual"},
                "output_signal": {"name": "signal-E", "type": "virtual"},
            }
        }

        combinator.set_arithmetic_conditions(
            first_operand=10, operation="or", second_operand=None
        )
        assert combinator.to_dict()["control_behavior"] == {
            "arithmetic_conditions": {"first_constant": 10, "operation": "OR"}
        }

        combinator.set_arithmetic_conditions(
            first_operand=None, second_operand=None, output_signal=None
        )
        assert "control_behavior" not in combinator.to_dict()

        combinator.set_arithmetic_conditions()
        assert "control_behavior" not in combinator.to_dict()

        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions(first_operand=TypeError)
        with pytest.raises(IncompleteSignalError):
            combinator.set_arithmetic_conditions(first_operand="incorrect")
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions(
                first_operand="signal-A",
                operation="incorrect",
                second_operand="signal-D",
            )
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions(
                first_operand="signal-A", operation="+", second_operand=TypeError
            )
        with pytest.raises(IncompleteSignalError):
            combinator.set_arithmetic_conditions(
                first_operand="signal-A", operation="+", second_operand="incorrect"
            )
        with pytest.raises(DataFormatError):
            combinator.set_arithmetic_conditions(
                first_operand="signal-A",
                operation="+",
                second_operand="signal-D",
                output_signal=TypeError,
            )
        with pytest.raises(IncompleteSignalError):
            combinator.set_arithmetic_conditions(
                first_operand="signal-A",
                operation="+",
                second_operand="signal-D",
                output_signal="incorrect",
            )

        combinator.set_arithmetic_conditions()
        assert "control_behavior" not in combinator.to_dict()

    def test_mergable(self):
        combinatorA = ArithmeticCombinator("arithmetic-combinator")
        combinatorB = ArithmeticCombinator("arithmetic-combinator")

        # Compatible
        assert combinatorA.mergable_with(combinatorB) == True

        combinatorB.set_arithmetic_conditions(
            "signal-A", {"red"}, "+", "signal-B", {"green"}, "signal-C"
        )
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
        combinatorB.set_arithmetic_conditions(
            "signal-A", {"red"}, "+", "signal-B", {"green"}, "signal-C"
        )

        combinatorA.merge(combinatorB)
        assert combinatorA.to_dict()["control_behavior"] == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "first_signal_networks": {"green": False},
                "operation": "+",
                "second_signal": {"name": "signal-B", "type": "virtual"},
                "second_signal_networks": {"red": False},
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        }

        # Test blueprint merging
        blueprint = Blueprint()
        blueprint.entities.append("arithmetic-combinator")

        entity_to_merge = ArithmeticCombinator("arithmetic-combinator")
        entity_to_merge.set_arithmetic_conditions(
            "signal-A", {"red"}, "+", "signal-B", {"green"}, "signal-C"
        )

        blueprint.entities.append(entity_to_merge, merge=True)

        assert len(blueprint.entities) == 1
        assert blueprint.entities[0].to_dict()["control_behavior"] == {
            "arithmetic_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "first_signal_networks": {"green": False},
                "operation": "+",
                "second_signal": {"name": "signal-B", "type": "virtual"},
                "second_signal_networks": {"red": False},
                "output_signal": {"name": "signal-C", "type": "virtual"},
            }
        }

        # Test dual-circuit-connections as well as self-reference
        group = Group()
        group.entities.append("arithmetic-combinator")
        group.add_circuit_connection("green", 0, 0, side_1="input", side_2="output")

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
            }
        ]
        assert blueprint.to_dict()["blueprint"]["wires"] == [[1, 2, 1, 4]]

    def test_eq(self):
        combinatorA = ArithmeticCombinator("arithmetic-combinator")
        combinatorB = ArithmeticCombinator("arithmetic-combinator")

        assert combinatorA == combinatorB

        combinatorA.set_arithmetic_conditions(
            1, {"red", "green"}, "*", 1, {"red", "green"}, "signal-check"
        )

        assert combinatorA != combinatorB

        container = Container("wooden-chest")

        assert combinatorA != container
        assert combinatorB != container

        # hashable
        assert isinstance(combinatorA, Hashable)
