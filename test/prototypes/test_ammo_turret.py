# test_ammo_turret.py

from draftsman.constants import Direction, Inventory
from draftsman.entity import AmmoTurret, ammo_turrets, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    AttrsSimpleCondition,
    TargetID,
    AttrsItemRequest,
    AttrsItemSpecification,
    AttrsInventoryLocation,
)
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_ammo_turret():
    if len(ammo_turrets) == 0:
        return None
    return AmmoTurret(
        "gun-turret",
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
        item_requests=[
            AttrsItemRequest(
                id="firearm-magazine",
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.turret_ammo, stack=0, count=200
                        )
                    ]
                ),
            )
        ],
        tags={"blah": "blah"},
    )


class TestAmmoTurret:
    def test_constructor_init(self):
        turret = AmmoTurret("gun-turret")
        turret.validate().reissue_all()
        assert turret.to_dict() == {
            "name": "gun-turret",
            "position": {"x": 1.0, "y": 1.0},
        }

        with pytest.warns(UnknownEntityWarning):
            turret = AmmoTurret("this is not a turret")
            turret.validate().reissue_all()

    def test_json_schema(self):
        assert AmmoTurret.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:ammo-turret",
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
                    "request. Items always go to the default inventory of that "
                    "object (if possible) in the order in which Factorio traverses "
                    "them.",
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }
        assert AmmoTurret.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:ammo-turret",
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

    def test_flags(self):
        turret = AmmoTurret("gun-turret")
        assert turret.rotatable == True
        assert turret.square == True
        # TODO: move
        # turret = AmmoTurret("flamethrower-turret")
        # assert turret.rotatable == True
        # assert turret.square == False

    def test_priority_condition(self):
        turret = AmmoTurret("gun-turret")
        turret.set_ignore_unlisted_targets_condition("signal-A", ">", "signal-B")
        assert turret.ignore_unlisted_targets_condition == AttrsSimpleCondition(
            first_signal="signal-A", comparator=">", second_signal="signal-B"
        )

    def test_target_priority_filters(self):
        turret = AmmoTurret("gun-turret")
        turret.priority_list = ["small-biter", "medium-biter"]
        assert turret.priority_list == [
            TargetID(index=0, name="small-biter"),
            TargetID(index=1, name="medium-biter"),
        ]
        assert turret.to_dict() == {
            "name": "gun-turret",
            "position": {"x": 1.0, "y": 1.0},
            "priority_list": [
                {
                    "index": 0,
                    "name": "small-biter",
                },
                {"index": 1, "name": "medium-biter"},
            ],
        }

        turret.priority_list = [
            {
                "index": 0,
                "name": "small-biter",
            },
            {"index": 1, "name": "medium-biter"},
        ]
        assert turret.priority_list == [
            TargetID(index=0, name="small-biter"),
            TargetID(index=1, name="medium-biter"),
        ]
        assert turret.to_dict() == {
            "name": "gun-turret",
            "position": {"x": 1.0, "y": 1.0},
            "priority_list": [
                {
                    "index": 0,
                    "name": "small-biter",
                },
                {"index": 1, "name": "medium-biter"},
            ],
        }

        with pytest.raises(DataFormatError):
            turret.priority_list = [TypeError]

    def test_mergable_with(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret", tags={"some": "stuff"})

        assert turret1.mergable_with(turret1)

        assert turret1.mergable_with(turret2)
        assert turret2.mergable_with(turret1)

        turret2.tile_position = (1, 1)
        assert not turret1.mergable_with(turret2)

    def test_merge(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret", tags={"some": "stuff"})

        turret1.merge(turret2)
        del turret2

        assert turret1.tags == {"some": "stuff"}

    def test_eq(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret")

        assert turret1 == turret2

        turret1.tags = {"some": "stuff"}

        assert turret1 != turret2

        container = Container()

        assert turret1 != container
        assert turret2 != container

        # hashable
        assert isinstance(turret1, Hashable)
