# test_artillery_wagon.py

from draftsman.constants import Inventory, Orientation
from draftsman.entity import ArtilleryWagon, artillery_wagons, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    AttrsItemRequest,
    AttrsItemSpecification,
    AttrsInventoryLocation,
    EquipmentComponent,
)
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_artillery_wagon():
    if len(artillery_wagons) == 0:
        return None
    return ArtilleryWagon(
        "artillery-wagon",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        orientation=Orientation.EAST,
        item_requests=[
            AttrsItemRequest(
                id="artillery-shell",
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.artillery_wagon_ammo, stack=0, count=1
                        )
                    ]
                ),
            ),
            AttrsItemRequest(
                id="energy-shield-equipment",
                items=AttrsItemSpecification(grid_count=1),
            ),
        ],
        equipment=[
            EquipmentComponent(equipment="energy-shield-equipment", position=(0, 0))
        ],
        enable_logistics_while_moving=False,
        auto_target=False,
        tags={"blah": "blah"},
        validate_assignment="none",  # Ignore the fact that this item has no equipment grid
    )


class TestArtilleryWagon:
    def test_constructor_init(self):
        artillery_wagon = ArtilleryWagon(
            "artillery-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
            enable_logistics_while_moving=False,
        )
        assert artillery_wagon.to_dict() == {
            "name": "artillery-wagon",
            "position": {"x": 1.0, "y": 1.0},
            "orientation": 0.75,
            "enable_logistics_while_moving": False,
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            ArtilleryWagon("this is not an artillery wagon").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            ArtilleryWagon(
                "artillery-wagon", orientation="wrong"
            ).validate().reissue_all()

    def test_json_schema(self):
        assert ArtilleryWagon.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:artillery-wagon",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {
                    "$ref": "urn:factorio:position",
                },
                "artillery_auto_targeting": {"type": "boolean", "default": "true"},
                "orientation": {"type": "number"},
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
        assert ArtilleryWagon.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:artillery-wagon",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {
                    "$ref": "urn:factorio:position",
                },
                "quality": {"$ref": "urn:factorio:quality-name"},
                "artillery_auto_targeting": {"type": "boolean", "default": "true"},
                "orientation": {"type": "number"},
                "items": {
                    "type": "array",
                    "items": {"$ref": "urn:factorio:item-request"},
                    "description": "A list of item requests objects, which contain "
                    "the item name, it's quality, the amount to request, as well as "
                    "exactly what inventories to request to and where inside those "
                    "inventories.",
                },
                "enable_logistics_while_moving": {"type": "boolean", "default": "true"},
                "grid": {
                    "type": "array",
                    "items": {"$ref": "urn:factorio:equipment-component"},
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }

    def test_mergable_with(self):
        wagon1 = ArtilleryWagon("artillery-wagon")
        wagon2 = ArtilleryWagon("artillery-wagon")

        assert wagon1.mergable_with(wagon2)
        assert wagon2.mergable_with(wagon1)

        wagon1.orientation = 0.5
        assert not wagon1.mergable_with(wagon2)

    def test_merge(self):
        wagon1 = ArtilleryWagon("artillery-wagon")
        wagon2 = ArtilleryWagon("artillery-wagon")
        wagon2.tags = {"some": "stuff"}

        wagon1.merge(wagon2)
        assert wagon1.tags == {"some": "stuff"}
        # Ensure wagon1's data remains valid even if wagon2 gets destroyed
        del wagon2
        assert wagon1.tags == {"some": "stuff"}

    def test_eq(self):
        wagon1 = ArtilleryWagon("artillery-wagon")
        wagon2 = ArtilleryWagon("artillery-wagon")

        assert wagon1 == wagon2

        wagon1.set_item_request("artillery-shell", 10)

        assert wagon1 != wagon2

        container = Container()

        assert wagon1 != container
        assert wagon2 != container

        # hashable
        assert isinstance(wagon1, Hashable)
