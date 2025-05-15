# test_fluid_turret.py

from draftsman.constants import Direction
from draftsman.prototypes.fluid_turret import (
    FluidTurret,
    fluid_turrets,
)
from draftsman.signatures import AttrsSimpleCondition
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_fluid_turret():
    if len(fluid_turrets) == 0:
        return None
    return FluidTurret(
        "flamethrower-turret",
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
        priority_list=["medium-biter"],
        ignore_unprioritized=True,
        set_priority_list=True,
        set_ignore_unprioritized=True,
        ignore_unlisted_targets_condition=AttrsSimpleCondition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        read_ammo=False,
        # item_requests=[
        #     AttrsItemRequest(
        #         id="firearm-magazine",
        #         items=AttrsItemSpecification(
        #             in_inventory=[
        #                 AttrsInventoryLocation(
        #                     inventory=Inventory.turret_ammo, stack=0, count=200
        #                 )
        #             ]
        #         ),
        #     )
        # ],
        tags={"blah": "blah"},
    )


def test_constructor():
    turret = FluidTurret("flamethrower-turret")

    with pytest.warns(UnknownEntityWarning):
        FluidTurret("not a fluid turret")


def test_json_schema():
    assert FluidTurret.json_schema(version=(1, 0)) == {
        "$id": "urn:factorio:entity:fluid-turret",
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
                "type": "object",
                "description": "A dictionary of item requests, where each key is "
                "the name of an item and the value is the count of that item to "
                "request. Items always go to the default inventory of that object "
                "(if possible) in the order in which Factorio traverses them.",
            },
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    }
    assert FluidTurret.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:fluid-turret",
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
            "items": {
                "type": "array",
                "items": {"$ref": "urn:factorio:item-request"},
                "description": "A list of item requests objects, which contain "
                "the item name, it's quality, the amount to request, as well as "
                "exactly what inventories to request to and where inside those "
                "inventories.",
            },
            "priority_list": {
                "type": "array",
                "items": {"$ref": "urn:factorio:target-id"},
            },
            "set_priority_list": {"type": "boolean", "default": "false"},
            "set_ignore_unprioritized": {"type": "boolean", "default": "false"},
            "ignore_unprioritized": {"type": "boolean", "default": "false"},
            "ignore_unlisted_targets_condition": {
                "$ref": "urn:factorio:simple-condition"
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
    for turret_name in fluid_turrets:
        turret = FluidTurret(turret_name)
        assert turret.power_connectable == False
        assert turret.dual_power_connectable == False
        assert turret.circuit_connectable == True
        assert turret.dual_circuit_connectable == False
