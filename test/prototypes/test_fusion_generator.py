# test_fusion_generator.py

from draftsman.constants import Direction
from draftsman.prototypes.fusion_generator import (
    FusionGenerator,
    fusion_generators,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_fusion_generator():
    if len(fusion_generators) == 0:
        return None
    return FusionGenerator(
        "fusion-generator",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


def test_constructor():
    generator = FusionGenerator("fusion-generator")

    with pytest.warns(UnknownEntityWarning):
        FusionGenerator("unknown fusion generator")


def test_json_schema():
    assert FusionGenerator.json_schema(version=(1, 0)) is None
    assert FusionGenerator.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:fusion-generator",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "entity_number": {"$ref": "urn:uint64"},
            "name": {"type": "string"},
            "position": {"$ref": "urn:factorio:position"},
            "quality": {"$ref": "urn:factorio:quality-name"},
            "direction": {"enum": list(range(16)), "default": 0},
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    }


def test_flags():
    for generator_name in fusion_generators:
        generator = FusionGenerator(generator_name)
        assert generator.power_connectable == False
        assert generator.dual_power_connectable == False
        assert generator.circuit_connectable == False
        assert generator.dual_circuit_connectable == False
