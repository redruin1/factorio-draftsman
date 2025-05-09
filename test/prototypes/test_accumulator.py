# test_accumulator.py

from draftsman.classes.vector import Vector
from draftsman.constants import ValidationMode
from draftsman.entity import Accumulator, accumulators, Container
from draftsman.error import DataFormatError, IncompleteSignalError
from draftsman.signatures import AttrsSignalID
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestAccumulator:
    def test_constructor_init(self):
        accumulator = Accumulator("accumulator", output_signal="signal-B")
        assert accumulator.to_dict() == {
            "name": accumulators[0],
            "position": accumulator.position.to_dict(),
            "control_behavior": {
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }
        accumulator = Accumulator(
            "accumulator", output_signal={"name": "signal-B", "type": "virtual"}
        )
        assert accumulator.to_dict() == {
            "name": accumulators[0],
            "position": accumulator.position.to_dict(),
            "control_behavior": {
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Accumulator("not an accumulator").validate().reissue_all()

        # Errors
        with pytest.raises(IncompleteSignalError):
            Accumulator(output_signal="incorrect").validate().reissue_all()

    def test_json_schema(self):
        assert Accumulator.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:accumulator",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "definitions": {
                "circuit-connection-point": {
                    "type": "object",
                    "properties": {
                        "entity_id": {"$ref": "urn:uint64"},
                        "circuit_id": {"enum": [1, 2]},
                    },
                    "required": ["entity_id"],
                },
                "wire-connection-point": {
                    "properties": {
                        "entity_id": {"$ref": "urn:uint64"},
                        "wire_id": {"enum": [0, 1]},
                    },
                    "required": ["entity_id"],
                },
            },
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {"$ref": "urn:factorio:position"},
                "connections": {
                    "1": {
                        "type": "object",
                        "properties": {
                            "red": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/circuit-connection-point"
                                },
                            },
                            "green": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/circuit-connection-point"
                                },
                            },
                        },
                    },
                    "2": {
                        "type": "object",
                        "properties": {
                            "red": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/circuit-connection-point"
                                },
                            },
                            "green": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/circuit-connection-point"
                                },
                            },
                        },
                    },
                    "Cu0": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/wire-connection-point"},
                    },
                    "Cu1": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/wire-connection-point"},
                    },
                },
                "control_behavior": {
                    "type": "object",
                    "properties": {
                        "output_signal": {
                            "anyOf": [
                                {"$ref": "urn:factorio:signal-id"},
                                {"type": "null"},
                            ]
                        }
                    },
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }
        assert Accumulator.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:accumulator",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {"$ref": "urn:factorio:position"},
                "quality": {"$ref": "urn:factorio:quality-name"},
                "control_behavior": {
                    "type": "object",
                    "properties": {
                        "output_signal": {
                            "anyOf": [
                                {"$ref": "urn:factorio:signal-id"},
                                {"type": "null"},
                            ]
                        }
                    },
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }

    def test_output_signal(self):
        accumulator = Accumulator()
        # String case
        accumulator.output_signal = "signal-D"
        assert accumulator.output_signal == AttrsSignalID(
            **{"name": "signal-D", "type": "virtual"}
        )

        # Dict case
        accumulator2 = Accumulator()
        accumulator2.output_signal = accumulator.output_signal
        assert accumulator2.output_signal == accumulator.output_signal

        # None case
        accumulator.output_signal = None
        assert accumulator.output_signal == None

        with pytest.raises(IncompleteSignalError):
            accumulator.output_signal = "incorrect"
        with pytest.raises(TypeError):
            accumulator.output_signal = {"incorrectly": "formatted"}

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
        assert accumulatorA.output_signal == AttrsSignalID(
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
