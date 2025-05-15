# test_fusion_reactor.py

from draftsman.constants import Direction
from draftsman.prototypes.fusion_reactor import (
    FusionReactor,
    fusion_reactors,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_fusion_reactor():
    if len(fusion_reactors) == 0:
        return None
    return FusionReactor(
        "fusion-reactor",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


def test_constructor():
    reactor = FusionReactor("fusion-reactor")

    with pytest.warns(UnknownEntityWarning):
        FusionReactor("unknown fusion reactor")


def test_json_schema():
    assert FusionReactor.json_schema(version=(1, 0)) is None
    assert FusionReactor.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:fusion-reactor",
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
    for reactor_name in fusion_reactors:
        reactor = FusionReactor(reactor_name)
        assert reactor.power_connectable == False
        assert reactor.dual_power_connectable == False
        assert reactor.circuit_connectable == False
        assert reactor.dual_circuit_connectable == False
