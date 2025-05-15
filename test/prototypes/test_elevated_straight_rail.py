# test_elevated_straight_rail.py

from draftsman.constants import Direction
from draftsman.prototypes.elevated_straight_rail import (
    ElevatedStraightRail,
    elevated_straight_rails,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_elevated_straight_rail():
    if len(elevated_straight_rails) == 0:
        return None
    return ElevatedStraightRail(
        "elevated-straight-rail",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


def test_constructor():
    rail = ElevatedStraightRail("elevated-straight-rail")

    with pytest.warns(UnknownEntityWarning):
        ElevatedStraightRail("unknown elevated straight rail")


def test_json_schema():
    assert ElevatedStraightRail.json_schema(version=(1, 0)) is None
    assert ElevatedStraightRail.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:elevated-straight-rail",
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
    for rail_name in elevated_straight_rails:
        print(rail_name)
        rail = ElevatedStraightRail(rail_name)
        assert rail.power_connectable == False
        assert rail.dual_power_connectable == False
        assert rail.circuit_connectable == False
        assert rail.dual_circuit_connectable == False
