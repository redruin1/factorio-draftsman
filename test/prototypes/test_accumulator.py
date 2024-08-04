# test_accumulator.py

from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.entity import Accumulator, accumulators, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalID
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestAccumulator:
    def test_constructor_init(self):
        accumulator = Accumulator(control_behavior={"output_signal": "signal-B"})
        assert accumulator.to_dict() == {
            "name": accumulators[0],
            "position": accumulator.position.to_dict(),
            "control_behavior": {
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }
        accumulator = Accumulator(
            control_behavior={"output_signal": {"name": "signal-B", "type": "virtual"}}
        )
        assert accumulator.to_dict() == {
            "name": accumulators[0],
            "position": accumulator.position.to_dict(),
            "control_behavior": {
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Accumulator(unused_keyword="whatever").validate().reissue_all()
        with pytest.warns(UnknownKeywordWarning):
            Accumulator(control_behavior={"unused_keyword": "whatever"}).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            Accumulator("not an accumulator").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            Accumulator(control_behavior="incorrect").validate().reissue_all()
        with pytest.raises(DataFormatError):
            Accumulator(control_behavior={"output_signal": "incorrect"}).validate().reissue_all()

    def test_output_signal(self):
        accumulator = Accumulator()
        # String case
        accumulator.output_signal = "signal-D"
        assert accumulator.output_signal == SignalID(
            **{"name": "signal-D", "type": "virtual"}
        )

        # Dict case
        accumulator2 = Accumulator()
        accumulator2.output_signal = accumulator.output_signal
        assert accumulator2.output_signal == accumulator.output_signal

        # None case
        accumulator.output_signal = None
        assert accumulator.output_signal == None

        with pytest.raises(DataFormatError):
            accumulator.output_signal = "incorrect"
        with pytest.raises(DataFormatError):
            accumulator.output_signal = {"incorrectly": "formatted"}

        accumulator.validate_assignment = "none"
        assert accumulator.validate_assignment == ValidationMode.NONE

        accumulator.output_signal = "incorrect"
        assert accumulator.output_signal == "incorrect"
        assert accumulator.to_dict() == {
            "name": "accumulator",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"output_signal": "incorrect"},
        }

    def test_mergable(self):
        accumulatorA = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB = Accumulator("accumulator", tile_position=(0, 0))

        # Compatible
        assert accumulatorA.mergable_with(accumulatorB) == True

        accumulatorA.output_signal = "signal-A"
        assert accumulatorA.mergable_with(accumulatorB) == True

        # Incompatible
        assert accumulatorA.mergable_with(Container()) == False

        accumulatorA.tile_position = (2, 0)
        assert accumulatorA.mergable_with(accumulatorB) == False

        accumulatorA.tile_position = (0, 0)
        accumulatorA.id = "something"
        assert accumulatorA.mergable_with(accumulatorB) == False

    def test_merge(self):
        accumulatorA = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB.output_signal = "signal-A"

        accumulatorA.merge(accumulatorB)
        assert accumulatorA.name == "accumulator"
        assert accumulatorA.tile_position == Vector(0, 0)
        assert accumulatorA.tile_position.to_dict() == {"x": 0, "y": 0}
        assert accumulatorA.output_signal == SignalID(
            **{"name": "signal-A", "type": "virtual"}
        )

    def test_eq(self):
        accumulatorA = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB = Accumulator("accumulator", tile_position=(0, 0))

        assert accumulatorA == accumulatorB

        accumulatorA.output_signal = "signal-B"  # Make sure it's not default!

        assert accumulatorA != accumulatorB

        container = Container("wooden-chest")

        assert accumulatorA != container
        assert accumulatorB != container

        # hashable
        assert isinstance(accumulatorA, Hashable)

    def test_json_schema(self):
        assert Accumulator.json_schema() == {
            "$defs": {
                "CircuitConnectionPoint": {
                    "additionalProperties": True,
                    "properties": {
                        "circuit_id": {
                            "anyOf": [
                                {"enum": [1, 2], "type": "integer"},
                                {"type": "null"},
                            ],
                            "default": None,
                            "title": "Circuit Id",
                        },
                        "entity_id": {
                            "exclusiveMaximum": 18446744073709551616,
                            "minimum": 0,
                            "title": "Entity Id",
                            "type": "integer",
                        },
                    },
                    "required": ["entity_id"],
                    "title": "CircuitConnectionPoint",
                    "type": "object",
                },
                "CircuitConnections": {
                    "additionalProperties": True,
                    "properties": {
                        "green": {
                            "anyOf": [
                                {
                                    "items": {"$ref": "#/$defs/CircuitConnectionPoint"},
                                    "type": "array",
                                },
                                {"type": "null"},
                            ],
                            "default": None,
                            "title": "Green",
                        },
                        "red": {
                            "anyOf": [
                                {
                                    "items": {"$ref": "#/$defs/CircuitConnectionPoint"},
                                    "type": "array",
                                },
                                {"type": "null"},
                            ],
                            "default": None,
                            "title": "Red",
                        },
                    },
                    "title": "CircuitConnections",
                    "type": "object",
                },
                "Connections": {
                    "additionalProperties": True,
                    "properties": {
                        "1": {
                            "anyOf": [
                                {"$ref": "#/$defs/CircuitConnections"},
                                {"type": "null"},
                            ],
                            "default": {"green": None, "red": None},
                        },
                        "2": {
                            "anyOf": [
                                {"$ref": "#/$defs/CircuitConnections"},
                                {"type": "null"},
                            ],
                            "default": {"green": None, "red": None},
                        },
                        "Cu0": {
                            "anyOf": [
                                {
                                    "items": {"$ref": "#/$defs/WireConnectionPoint"},
                                    "type": "array",
                                },
                                {"type": "null"},
                            ],
                            "default": None,
                            "title": "Cu0",
                        },
                        "Cu1": {
                            "anyOf": [
                                {
                                    "items": {"$ref": "#/$defs/WireConnectionPoint"},
                                    "type": "array",
                                },
                                {"type": "null"},
                            ],
                            "default": None,
                            "title": "Cu1",
                        },
                    },
                    "title": "Connections",
                    "type": "object",
                },
                "ControlBehavior": {
                    "additionalProperties": True,
                    "properties": {
                        "output_signal": {
                            "anyOf": [{"$ref": "#/$defs/SignalID"}, {"type": "null"}],
                            "default": {"name": "signal-A", "type": "virtual"},
                            "description": "The output signal to broadcast this accumulators charge level as\n"
                            "to any connected circuit network. The output value is as a \n"
                            "percentage, where '0' is empty and '100' is full.",
                        }
                    },
                    "title": "ControlBehavior",
                    "type": "object",
                },
                "FloatPosition": {
                    "additionalProperties": True,
                    "properties": {
                        "x": {"title": "X", "type": "number"},
                        "y": {"title": "Y", "type": "number"},
                    },
                    "required": ["x", "y"],
                    "title": "FloatPosition",
                    "type": "object",
                },
                "SignalID": {
                    "additionalProperties": True,
                    "properties": {
                        "name": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "description": "Name of the signal. If omitted, the signal is treated as no signal and \n"
                            "removed on import/export cycle.",
                            "title": "Name",
                        },
                        "type": {
                            "description": "Category of the signal.",
                            "enum": ["item", "fluid", "virtual"],
                            "title": "Type",
                            "type": "string",
                        },
                    },
                    "required": ["name", "type"],
                    "title": "SignalID",
                    "type": "object",
                },
                "WireConnectionPoint": {
                    "additionalProperties": True,
                    "properties": {
                        "entity_id": {
                            "exclusiveMaximum": 18446744073709551616,
                            "minimum": 0,
                            "title": "Entity Id",
                            "type": "integer",
                        },
                        "wire_id": {
                            "anyOf": [
                                {"enum": [0, 1], "type": "integer"},
                                {"type": "null"},
                            ],
                            "default": None,
                            "title": "Wire Id",
                        },
                    },
                    "required": ["entity_id"],
                    "title": "WireConnectionPoint",
                    "type": "object",
                },
            },
            "additionalProperties": True,
            "properties": {
                "connections": {
                    "anyOf": [{"$ref": "#/$defs/Connections"}, {"type": "null"}],
                    "default": {
                        "1": {"green": None, "red": None},
                        "2": {"green": None, "red": None},
                        "Cu0": None,
                        "Cu1": None,
                    },
                    "description": "All circuit and copper wire connections that this entity has. Note\n"
                    "that copper wire connections in this field are exclusively for \n"
                    "power-switch connections; for power-pole to power-pole connections \n"
                    "see the 'neighbours' key.",
                },
                "control_behavior": {
                    "anyOf": [{"$ref": "#/$defs/ControlBehavior"}, {"type": "null"}],
                    "default": {
                        "output_signal": {"name": "signal-A", "type": "virtual"}
                    },
                },
                "entity_number": {
                    "description": "The number of the entity in it's parent blueprint, 1-based. In\n"
                    "practice this is the index of the dictionary in the blueprint's \n"
                    "'entities' list, but this is not enforced.\n"
                    "\n"
                    "NOTE: The range of this number is described as a 64-bit unsigned int,\n"
                    "but due to limitations with Factorio's PropertyTree implementation,\n"
                    "values above 2^53 will suffer from floating-point precision error.\n"
                    "See here: https://forums.factorio.com/viewtopic.php?p=592165#p592165",
                    "exclusiveMaximum": 18446744073709551616,
                    "minimum": 0,
                    "title": "Entity Number",
                    "type": "integer",
                },
                "name": {
                    "description": "The internal ID of the entity.",
                    "title": "Name",
                    "type": "string",
                },
                "position": {
                    "allOf": [{"$ref": "#/$defs/FloatPosition"}],
                    "description": "The position of the entity, almost always measured from it's center. \n"
                    "Uses Factorio tiles as its unit.",
                },
                "tags": {
                    "anyOf": [{"type": "object"}, {"type": "null"}],
                    "default": {},
                    "description": "Any other additional metadata associated with this blueprint entity. \n"
                    "Frequently used by mods.",
                    "title": "Tags",
                },
            },
            "required": ["name", "position", "entity_number"],
            "title": "Accumulator",
            "type": "object",
        }
