# test_artillery_turret.py

from draftsman.constants import Direction, Inventory
from draftsman.prototypes.artillery_turret import (
    ArtilleryTurret,
    artillery_turrets,
)
from draftsman.signatures import AttrsSimpleCondition, AttrsItemRequest, AttrsItemSpecification, AttrsInventoryLocation
from draftsman.warning import UnknownEntityWarning

import pytest


valid_artillery_turret = ArtilleryTurret(
    "artillery-turret",
    id="test",
    quality="uncommon",
    tile_position=(1, 1),
    direction=Direction.EAST,
    circuit_enabled=True,
    circuit_condition=AttrsSimpleCondition(
        first_signal="signal-A", comparator="<", second_signal="signal-B"
    ),
    connect_to_logistic_network=True,
    logistic_condition=AttrsSimpleCondition(
        first_signal="signal-A", comparator="<", second_signal="signal-B"
    ),
    read_ammo=False,
    item_requests=[
        AttrsItemRequest(
            id="artillery-shell",
            items=AttrsItemSpecification(
                in_inventory=[
                    AttrsInventoryLocation(
                        inventory=Inventory.artillery_turret_ammo, stack=0, count=1
                    )
                ]
            ),
        )
    ],
    tags={"blah": "blah"}
)


def test_constructor():
    turret = ArtilleryTurret("artillery-turret")

    with pytest.warns(UnknownEntityWarning):
        ArtilleryTurret("unknown artillery turret")


def test_json_schema():
    assert ArtilleryTurret.json_schema(version=(1, 0)) == {
        "$id": "urn:factorio:entity:artillery-turret",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "entity_number": {"$ref": "urn:uint64"},
            "name": {"type": "string"},
            "position": {
                "$ref": "urn:factorio:position",
            },
            "direction": {"enum": list(range(8)), "default": 0},
            "items": {
                "type": "array",
                "items": {"$ref": "urn:factorio:item-request"},
            },
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    }
    assert ArtilleryTurret.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:artillery-turret",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "entity_number": {"$ref": "urn:uint64"},
            "name": {"type": "string"},
            "position": {
                "$ref": "urn:factorio:position",
            },
            "quality": {"$ref": "urn:factorio:quality-name"},
            "direction": {"enum": list(range(16)), "default": 0},
            "artillery_auto_targeting": {"type": "boolean", "default": "true"},
            "items": {
                "type": "array",
                "items": {"$ref": "urn:factorio:item-request"},
            },
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
                    "read_ammo": {"type": "boolean", "default": "true"},
                },
                "description": "Entity-specific structure which holds keys related to configuring how this entity acts.",
            },
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    }


def test_flags():
    for turret_name in artillery_turrets:
        turret = ArtilleryTurret(turret_name)
        assert turret.power_connectable == False
        assert turret.dual_power_connectable == False
        assert turret.circuit_connectable == True
        assert turret.dual_circuit_connectable == False
