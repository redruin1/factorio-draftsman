# test_artillery_turret.py

from draftsman.prototypes.artillery_turret import (
    ArtilleryTurret,
    artillery_turrets,
)
from draftsman.warning import UnknownEntityWarning

import pytest


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
