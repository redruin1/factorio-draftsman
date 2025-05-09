# test_arithmetic_combinator.py

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction, ValidationMode
from draftsman.entity import ArithmeticCombinator, arithmetic_combinators, Container
from draftsman.error import DataFormatError, IncompleteSignalError
from draftsman.signatures import AttrsSignalID
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    PureVirtualDisallowedWarning,
    SignalConfigurationWarning,
    UnknownSignalWarning,
)

from collections.abc import Hashable
import pytest


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
            "direction": 4,
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
            "direction": 4,
            "player_description": None,
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
        assert combinator.first_operand == AttrsSignalID(
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
        assert combinator.first_operand == AttrsSignalID(
            name="signal-each", type="virtual"
        )
        assert combinator.output_signal == AttrsSignalID(
            name="signal-each", type="virtual"
        )

        # Setting to the same signal should issue no warnings
        combinator.first_operand = "signal-each"
        assert combinator.first_operand == AttrsSignalID(
            name="signal-each", type="virtual"
        )

        # Setting to non special should issue a warning, but not remove the output
        # TODO: reimplement
        # with pytest.warns(SignalConfigurationWarning):
        #     combinator.first_operand = "signal-A"
        # assert combinator.first_operand == AttrsSignalID(name="signal-A", type="virtual")
        # assert combinator.output_signal == AttrsSignalID(name="signal-each", type="virtual")

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
        assert combinator.second_operand == AttrsSignalID(
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
        assert combinator.second_operand == AttrsSignalID(
            name="signal-each", type="virtual"
        )
        assert combinator.output_signal == AttrsSignalID(
            name="signal-each", type="virtual"
        )

        # Setting to the same signal should issue no warnings
        combinator.second_operand = "signal-each"
        assert combinator.second_operand == AttrsSignalID(
            name="signal-each", type="virtual"
        )

        # Setting to non special should issue a warning, but not remove the output
        # TODO: reimplement
        # with pytest.warns(SignalConfigurationWarning):
        #     combinator.second_operand = "signal-A"
        # assert combinator.second_operand == AttrsSignalID(name="signal-A", type="virtual")
        # assert combinator.output_signal == AttrsSignalID(name="signal-each", type="virtual")

    def test_set_output_signal(self):
        combinator = ArithmeticCombinator("arithmetic-combinator")
        assert combinator.output_signal == None

        combinator.output_signal = "signal-A"
        assert combinator.output_signal == AttrsSignalID(
            **{"name": "signal-A", "type": "virtual"}
        )

        combinator.output_signal = {"name": "signal-B", "type": "virtual"}
        assert combinator.output_signal == AttrsSignalID(
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

        combinator.validate_assignment = "minimum"
        assert combinator.validate_assignment is ValidationMode.MINIMUM

        # No warnings
        combinator.output_signal = "signal-everything"
        assert combinator.output_signal == AttrsSignalID(
            name="signal-everything", type="virtual"
        )
        combinator.output_signal = "signal-each"
        assert combinator.output_signal == AttrsSignalID(
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

    # def test_json_schema(self):
    #     assert ArithmeticCombinator.json_schema() == {
    #         "$defs": {
    #             "ArithmeticConditions": {
    #                 "additionalProperties": True,
    #                 "properties": {
    #                     "first_constant": {
    #                         "anyOf": [
    #                             {
    #                                 "exclusiveMaximum": 2147483648,
    #                                 "minimum": -2147483648,
    #                                 "type": "integer",
    #                             },
    #                             {"type": "null"},
    #                         ],
    #                         "default": None,
    #                         "description": "The constant value located in the left slot, if present.",
    #                         "title": "First Constant",
    #                     },
    #                     "first_signal": {
    #                         "anyOf": [{"$ref": "#/$defs/SignalID"}, {"type": "null"}],
    #                         "default": None,
    #                         "description": "The signal type located in the left slot, if present. If\nboth this key and 'first_constant' are defined, this key\ntakes precedence.",
    #                     },
    #                     "operation": {
    #                         "default": "*",
    #                         "description": "The operation to perform on the two operands.",
    #                         "enum": [
    #                             "*",
    #                             "/",
    #                             "+",
    #                             "-",
    #                             "%",
    #                             "^",
    #                             "<<",
    #                             ">>",
    #                             "AND",
    #                             "OR",
    #                             "XOR",
    #                             None,
    #                         ],
    #                         "title": "Operation",
    #                     },
    #                     "second_constant": {
    #                         "anyOf": [
    #                             {
    #                                 "exclusiveMaximum": 2147483648,
    #                                 "minimum": -2147483648,
    #                                 "type": "integer",
    #                             },
    #                             {"type": "null"},
    #                         ],
    #                         "default": 0,
    #                         "description": "The constant value located in the right slot, if present.",
    #                         "title": "Second Constant",
    #                     },
    #                     "second_signal": {
    #                         "anyOf": [{"$ref": "#/$defs/SignalID"}, {"type": "null"}],
    #                         "default": None,
    #                         "description": "The signal type located in the right slot, if present. If\nboth this key and 'second_constant' are defined, this key\ntakes precedence.",
    #                     },
    #                     "output_signal": {
    #                         "anyOf": [{"$ref": "#/$defs/SignalID"}, {"type": "null"}],
    #                         "default": None,
    #                         "description": "The output signal to emit the operation result as. Can be\n'signal-each', but only if one of 'first_signal' or \n'second_signal' is also 'signal-each'. No other pure virtual\nsignals are permitted in arithmetic combinators.",
    #                     },
    #                 },
    #                 "title": "ArithmeticConditions",
    #                 "type": "object",
    #             },
    #             "CircuitConnectionPoint": {
    #                 "additionalProperties": True,
    #                 "properties": {
    #                     "entity_id": {
    #                         "exclusiveMaximum": 18446744073709551616,
    #                         "minimum": 0,
    #                         "title": "Entity Id",
    #                         "type": "integer",
    #                     },
    #                     "circuit_id": {
    #                         "anyOf": [
    #                             {"enum": [1, 2], "type": "integer"},
    #                             {"type": "null"},
    #                         ],
    #                         "default": None,
    #                         "title": "Circuit Id",
    #                     },
    #                 },
    #                 "required": ["entity_id"],
    #                 "title": "CircuitConnectionPoint",
    #                 "type": "object",
    #             },
    #             "CircuitConnections": {
    #                 "additionalProperties": True,
    #                 "properties": {
    #                     "red": {
    #                         "anyOf": [
    #                             {
    #                                 "items": {"$ref": "#/$defs/CircuitConnectionPoint"},
    #                                 "type": "array",
    #                             },
    #                             {"type": "null"},
    #                         ],
    #                         "default": None,
    #                         "title": "Red",
    #                     },
    #                     "green": {
    #                         "anyOf": [
    #                             {
    #                                 "items": {"$ref": "#/$defs/CircuitConnectionPoint"},
    #                                 "type": "array",
    #                             },
    #                             {"type": "null"},
    #                         ],
    #                         "default": None,
    #                         "title": "Green",
    #                     },
    #                 },
    #                 "title": "CircuitConnections",
    #                 "type": "object",
    #             },
    #             "Connections": {
    #                 "additionalProperties": True,
    #                 "properties": {
    #                     "1": {
    #                         "anyOf": [
    #                             {"$ref": "#/$defs/CircuitConnections"},
    #                             {"type": "null"},
    #                         ],
    #                         "default": {"green": None, "red": None},
    #                     },
    #                     "2": {
    #                         "anyOf": [
    #                             {"$ref": "#/$defs/CircuitConnections"},
    #                             {"type": "null"},
    #                         ],
    #                         "default": {"green": None, "red": None},
    #                     },
    #                     "Cu0": {
    #                         "anyOf": [
    #                             {
    #                                 "items": {"$ref": "#/$defs/WireConnectionPoint"},
    #                                 "type": "array",
    #                             },
    #                             {"type": "null"},
    #                         ],
    #                         "default": None,
    #                         "title": "Cu0",
    #                     },
    #                     "Cu1": {
    #                         "anyOf": [
    #                             {
    #                                 "items": {"$ref": "#/$defs/WireConnectionPoint"},
    #                                 "type": "array",
    #                             },
    #                             {"type": "null"},
    #                         ],
    #                         "default": None,
    #                         "title": "Cu1",
    #                     },
    #                 },
    #                 "title": "Connections",
    #                 "type": "object",
    #             },
    #             "ControlBehavior": {
    #                 "additionalProperties": True,
    #                 "properties": {
    #                     "arithmetic_conditions": {
    #                         "anyOf": [
    #                             {"$ref": "#/$defs/ArithmeticConditions"},
    #                             {"type": "null"},
    #                         ],
    #                         "default": {
    #                             "first_constant": None,
    #                             "first_signal": None,
    #                             "operation": "*",
    #                             "output_signal": None,
    #                             "second_constant": 0,
    #                             "second_signal": None,
    #                         },
    #                     }
    #                 },
    #                 "title": "ControlBehavior",
    #                 "type": "object",
    #             },
    #             "FloatPosition": {
    #                 "additionalProperties": True,
    #                 "properties": {
    #                     "x": {"title": "X", "type": "number"},
    #                     "y": {"title": "Y", "type": "number"},
    #                 },
    #                 "required": ["x", "y"],
    #                 "title": "FloatPosition",
    #                 "type": "object",
    #             },
    #             "SignalID": {
    #                 "additionalProperties": True,
    #                 "properties": {
    #                     "name": {
    #                         "anyOf": [{"type": "string"}, {"type": "null"}],
    #                         "description": "Name of the signal. If omitted, the signal is treated as no signal and \nremoved on import/export cycle.",
    #                         "title": "Name",
    #                     },
    #                     "type": {
    #                         "description": "Category of the signal.",
    #                         "enum": ["item", "fluid", "virtual"],
    #                         "title": "Type",
    #                         "type": "string",
    #                     },
    #                 },
    #                 "required": ["name", "type"],
    #                 "title": "SignalID",
    #                 "type": "object",
    #             },
    #             "WireConnectionPoint": {
    #                 "additionalProperties": True,
    #                 "properties": {
    #                     "entity_id": {
    #                         "exclusiveMaximum": 18446744073709551616,
    #                         "minimum": 0,
    #                         "title": "Entity Id",
    #                         "type": "integer",
    #                     },
    #                     "wire_id": {
    #                         "anyOf": [
    #                             {"enum": [0, 1], "type": "integer"},
    #                             {"type": "null"},
    #                         ],
    #                         "default": None,
    #                         "title": "Wire Id",
    #                     },
    #                 },
    #                 "required": ["entity_id"],
    #                 "title": "WireConnectionPoint",
    #                 "type": "object",
    #             },
    #             "draftsman__constants__Direction__2": {
    #                 "$ref": "#/$defs/draftsman__constants__Direction__1"
    #             },
    #             "draftsman__constants__Direction__1": {
    #                 "description": "Factorio direction enum. Encompasses all 8 cardinal directions and diagonals\nin the range [0, 7] where north is 0 and increments clockwise. Provides a\nnumber of convenience constants and functions over working with a raw int\nvalue.\n\n* ``NORTH`` (0) (Default)\n* ``NORTHEAST`` (1)\n* ``EAST`` (2)\n* ``SOUTHEAST`` (3)\n* ``SOUTH`` (4)\n* ``SOUTHWEST`` (5)\n* ``WEST`` (6)\n* ``NORTHWEST`` (7)",
    #                 "enum": [0, 1, 2, 3, 4, 5, 6, 7],
    #                 "title": "Direction",
    #                 "type": "integer",
    #             },
    #         },
    #         "additionalProperties": True,
    #         "properties": {
    #             "name": {
    #                 "description": "The internal ID of the entity.",
    #                 "title": "Name",
    #                 "type": "string",
    #             },
    #             "position": {
    #                 "allOf": [{"$ref": "#/$defs/FloatPosition"}],
    #                 "description": "The position of the entity, almost always measured from it's center. \nMeasured in Factorio tiles.",
    #             },
    #             "entity_number": {
    #                 "description": "The number of the entity in it's parent blueprint, 1-based. In\npractice this is the index of the dictionary in the blueprint's \n'entities' list, but this is not enforced.\n\nNOTE: The range of this number is described as a 64-bit unsigned int,\nbut due to limitations with Factorio's PropertyTree implementation,\nvalues above 2^53 will suffer from floating-point precision error.\nSee here: https://forums.factorio.com/viewtopic.php?p=592165#p592165",
    #                 "exclusiveMaximum": 18446744073709551616,
    #                 "minimum": 0,
    #                 "title": "Entity Number",
    #                 "type": "integer",
    #             },
    #             "tags": {
    #                 "anyOf": [{"type": "object"}, {"type": "null"}],
    #                 "default": {},
    #                 "description": "Any other additional metadata associated with this blueprint entity. \nFrequently used by mods.",
    #                 "title": "Tags",
    #             },
    #             "direction": {
    #                 "anyOf": [
    #                     {"$ref": "#/$defs/draftsman__constants__Direction__2"},
    #                     {"type": "null"},
    #                 ],
    #                 "default": 0,
    #                 "description": "The grid-aligned direction this entity is facing. Direction can only\nbe one of 4 distinct (cardinal) directions, which differs from \n'orientation' which is used for RollingStock.",
    #             },
    #             "connections": {
    #                 "anyOf": [{"$ref": "#/$defs/Connections"}, {"type": "null"}],
    #                 "default": {
    #                     "1": {"green": None, "red": None},
    #                     "2": {"green": None, "red": None},
    #                     "Cu0": None,
    #                     "Cu1": None,
    #                 },
    #                 "description": "All circuit and copper wire connections that this entity has. Note\nthat copper wire connections in this field are exclusively for \npower-switch connections; for power-pole to power-pole connections \nsee the 'neighbours' key.",
    #             },
    #             "control_behavior": {
    #                 "anyOf": [{"$ref": "#/$defs/ControlBehavior"}, {"type": "null"}],
    #                 "default": {
    #                     "arithmetic_conditions": {
    #                         "first_constant": None,
    #                         "first_signal": None,
    #                         "operation": "*",
    #                         "output_signal": None,
    #                         "second_constant": 0,
    #                         "second_signal": None,
    #                     }
    #                 },
    #             },
    #         },
    #         "required": ["name", "position", "entity_number"],
    #         "title": "ArithmeticCombinator",
    #         "type": "object",
    #     }
