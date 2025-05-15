# test_elevated_curved_rail_a.py

from draftsman.constants import Direction
from draftsman.prototypes.elevated_curved_rail_a import (
    ElevatedCurvedRailA,
    elevated_curved_rails_a,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_elevated_curved_rail_a():
    if len(elevated_curved_rails_a) == 0:
        return None
    return ElevatedCurvedRailA(
        "elevated-curved-rail-a",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


def test_constructor():
    curved_rail = ElevatedCurvedRailA("elevated-curved-rail-a")

    with pytest.warns(UnknownEntityWarning):
        ElevatedCurvedRailA("unknown curved rail")


def test_json_schema():
    assert ElevatedCurvedRailA.json_schema(version=(1, 0)) is None
    assert ElevatedCurvedRailA.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:elevated-curved-rail-a",
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
    for rail_name in elevated_curved_rails_a:
        curved_rail = ElevatedCurvedRailA(rail_name)
        assert curved_rail.power_connectable == False
        assert curved_rail.dual_power_connectable == False
        assert curved_rail.circuit_connectable == False
        assert curved_rail.dual_circuit_connectable == False
