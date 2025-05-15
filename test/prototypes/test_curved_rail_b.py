# test_curved_rail_b.py

from draftsman.constants import Direction
from draftsman.prototypes.curved_rail_b import (
    CurvedRailB,
    curved_rails_b,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_curved_rail_b():
    if len(curved_rails_b) == 0:
        return None
    return CurvedRailB(
        "curved-rail-b",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


def test_constructor():
    curved_rail = CurvedRailB("curved-rail-b")

    with pytest.warns(UnknownEntityWarning):
        CurvedRailB("unknown curved rail")


def test_json_schema():
    assert CurvedRailB.json_schema(version=(1, 0)) is None
    assert CurvedRailB.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:curved-rail-b",
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
    for rail_name in curved_rails_b:
        curved_rail = CurvedRailB(rail_name)
        assert curved_rail.power_connectable == False
        assert curved_rail.dual_power_connectable == False
        assert curved_rail.circuit_connectable == False
        assert curved_rail.dual_circuit_connectable == False
