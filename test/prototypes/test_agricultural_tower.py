# test_agricultural_tower.py

from draftsman.prototypes.agricultural_tower import (
    AgriculturalTower,
    agricultural_towers,
)
from draftsman.signatures import AttrsSimpleCondition
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_agricultural_tower():
    if len(agricultural_towers) == 0:
        return None
    return AgriculturalTower(
        "agricultural-tower",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        circuit_condition=AttrsSimpleCondition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        connect_to_logistic_network=True,
        logistic_condition=AttrsSimpleCondition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        read_contents=True,
        tags={"blah": "blah"},
    )


def test_constructor():
    tower = AgriculturalTower("agricultural-tower")
    assert tower.to_dict() == {
        "name": "agricultural-tower",
        "position": {"x": 1.5, "y": 1.5},
    }

    with pytest.warns(UnknownEntityWarning):
        AgriculturalTower("unknown agricultural tower")


def test_flags():
    for tower_name in agricultural_towers:
        tower = AgriculturalTower(tower_name)
        assert tower.power_connectable == False
        assert tower.dual_power_connectable == False
        assert tower.circuit_connectable == True
        assert tower.dual_circuit_connectable == False


def test_json_schema():
    assert AgriculturalTower.json_schema(version=(1, 0)) == None
    assert AgriculturalTower.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:agricultural-tower",
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
                    "circuit_enabled": {"type": "boolean", "default": "false"},
                    "circuit_condition": {"$ref": "urn:factorio:simple-condition"},
                    "connect_to_logistic_network": {
                        "type": "boolean",
                        "default": "false",
                    },
                    "logistic_condition": {"$ref": "urn:factorio:simple-condition"},
                    "read_contents": {"type": "boolean", "default": "false"},
                },
                "description": "Entity-specific structure which holds keys related to configuring how this entity acts.",
            },
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    }
