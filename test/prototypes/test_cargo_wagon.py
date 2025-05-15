# test_cargo_wagon.py

from draftsman.constants import Inventory, Orientation, ValidationMode
from draftsman.entity import CargoWagon, cargo_wagons, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    AttrsItemFilter,
    AttrsItemRequest,
    AttrsItemSpecification,
    AttrsInventoryLocation,
    EquipmentComponent,
)
from draftsman.warning import (
    BarWarning,
    EquipmentGridWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_cargo_wagon():
    if len(cargo_wagons) == 0:
        return None
    return CargoWagon(
        "cargo-wagon",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        orientation=Orientation.EAST,
        inventory_filters=[AttrsItemFilter(index=0, name="iron-ore")],
        bar=10,
        item_requests=[
            AttrsItemRequest(
                id="iron-ore",
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.cargo_wagon, stack=0, count=50
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
        tags={"blah": "blah"},
        validate_assignment="none",
    )


class TestCargoWagon:
    def test_constructor_init(self):
        cargo_wagon = CargoWagon(
            "cargo-wagon",
            tile_position=[0, 0],
            bar=0,
        )
        assert cargo_wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
            "inventory": {"bar": 0},
        }

        cargo_wagon = CargoWagon(
            "cargo-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
            bar=10,
            inventory_filters=["transport-belt", "transport-belt", "transport-belt"],
        )
        assert cargo_wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 1.0},
            "orientation": 0.75,
            "inventory": {
                "bar": 10,
                "filters": [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "transport-belt"},
                    {"index": 3, "name": "transport-belt"},
                ],
            },
        }

        cargo_wagon = CargoWagon(
            "cargo-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
            bar=10,
            inventory_filters=[
                {"index": 0, "name": "transport-belt"},
                {"index": 1, "name": "transport-belt"},
                {"index": 2, "name": "transport-belt"},
            ],
        )
        assert cargo_wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 1.0},
            "orientation": 0.75,
            "inventory": {
                "bar": 10,
                "filters": [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "transport-belt"},
                    {"index": 3, "name": "transport-belt"},
                ],
            },
        }

        # Warnings
        # Warn if the cargo wagon is not on a rail (close enough to one?)
        # TODO (Complex)
        with pytest.warns(UnknownEntityWarning):
            CargoWagon("this is not a cargo-wagon").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            CargoWagon("cargo-wagon", orientation="wrong").validate().reissue_all()

    def test_json_schema(self):
        assert CargoWagon.json_schema(version=(1, 0)) == {
            "$id": "urn:factorio:entity:cargo-wagon",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {
                    "$ref": "urn:factorio:position",
                },
                "orientation": {"type": "number"},
                "inventory": {
                    "type": "object",
                    "properties": {
                        "bar": {"oneOf": [{"$ref": "urn:uint16"}, {"type": "null"}]},
                        "filters": {
                            "type": "array",
                            "items": {"$ref": "urn:factorio:item-filter"},
                        },
                    },
                },
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
        assert CargoWagon.json_schema(version=(2, 0)) == {
            "$id": "urn:factorio:entity:cargo-wagon",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "entity_number": {"$ref": "urn:uint64"},
                "name": {"type": "string"},
                "position": {
                    "$ref": "urn:factorio:position",
                },
                "quality": {"$ref": "urn:factorio:quality-name"},
                "inventory": {
                    "type": "object",
                    "properties": {
                        "bar": {"oneOf": [{"$ref": "urn:uint16"}, {"type": "null"}]},
                        "filters": {
                            "type": "array",
                            "items": {"$ref": "urn:factorio:item-filter"},
                        },
                    },
                },
                "enable_logistics_while_moving": {"type": "boolean", "default": "true"},
                "grid": {
                    "type": "array",
                    "items": {"$ref": "urn:factorio:equipment-component"},
                },
                "orientation": {"type": "number"},
                "items": {
                    "type": "array",
                    "items": {"$ref": "urn:factorio:item-request"},
                    "description": "A list of item requests objects, which contain "
                    "the item name, it's quality, the amount to request, as well as "
                    "exactly what inventories to request to and where inside those "
                    "inventories.",
                },
                "tags": {"type": "object"},
            },
            "required": ["entity_number", "name", "position"],
        }

    def test_equipment_grid(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.equipment_grid is None

        with pytest.warns(EquipmentGridWarning):
            wagon.add_equipment("roboport")

    def test_set_orientation(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.orientation == Orientation.NORTH
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
        }

        wagon.orientation = 0.0
        assert wagon.orientation == Orientation.NORTH
        assert wagon.collision_set.shapes[0].angle == 0
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
        }

        # Unknown wagon
        wagon = CargoWagon(
            "unknown-cargo-wagon", validate_assignment=ValidationMode.MINIMUM
        )
        assert wagon.orientation == Orientation.NORTH
        assert wagon.collision_set is None
        assert wagon.to_dict() == {
            "name": "unknown-cargo-wagon",
            "position": {"x": 0.0, "y": 0.0},
        }

        wagon.orientation = Orientation.WEST
        assert wagon.orientation == Orientation.WEST

        with pytest.raises(DataFormatError):
            wagon.orientation = "incorrect"

    def test_set_inventory_filters(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.inventory_filters == []
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
        }

        # Shorthand format
        wagon.inventory_filters = ["iron-ore", "copper-ore", "iron-ore"]
        assert wagon.inventory_filters == [
            AttrsItemFilter(**{"index": 0, "name": "iron-ore"}),
            AttrsItemFilter(**{"index": 1, "name": "copper-ore"}),
            AttrsItemFilter(**{"index": 2, "name": "iron-ore"}),
        ]
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
            "inventory": {
                "filters": [
                    {"index": 1, "name": "iron-ore"},
                    {"index": 2, "name": "copper-ore"},
                    {"index": 3, "name": "iron-ore"},
                ]
            },
        }

        # Explicit format
        wagon.inventory_filters = [
            {"index": 0, "name": "iron-ore"},
            {"index": 1, "name": "copper-ore"},
            {"index": 2, "name": "iron-ore"},
        ]
        assert wagon.inventory_filters == [
            AttrsItemFilter(**{"index": 0, "name": "iron-ore"}),
            AttrsItemFilter(**{"index": 1, "name": "copper-ore"}),
            AttrsItemFilter(**{"index": 2, "name": "iron-ore"}),
        ]
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
            "inventory": {
                "filters": [
                    {"index": 1, "name": "iron-ore"},
                    {"index": 2, "name": "copper-ore"},
                    {"index": 3, "name": "iron-ore"},
                ]
            },
        }

        with pytest.warns(UnknownItemWarning):
            wagon.inventory_filters = ["unknown"]
            assert wagon.inventory_filters == [
                AttrsItemFilter(**{"index": 0, "name": "unknown"}),
            ]

        with pytest.raises(DataFormatError):
            wagon.inventory_filters = "incorrect"
        assert wagon.inventory_filters[0].name == "unknown"

        wagon.validate_assignment = "none"
        assert wagon.validate_assignment == ValidationMode.NONE

    def test_set_inventory_filter(self):
        wagon = CargoWagon("cargo-wagon")

        wagon.set_inventory_filter(0, "wooden-chest")
        assert wagon.inventory_filters == [
            AttrsItemFilter(**{"index": 0, "name": "wooden-chest"}),
        ]

        # Replace existing
        wagon.set_inventory_filter(0, "iron-chest")
        assert wagon.inventory_filters == [
            AttrsItemFilter(**{"index": 0, "name": "iron-chest"}),
        ]

        # Remove existing
        wagon.set_inventory_filter(0, None)
        assert wagon.inventory_filters == []

        # Ensure errors even if validation is off
        wagon.validate_assignment = "none"
        assert wagon.validate_assignment == ValidationMode.NONE
        with pytest.raises(DataFormatError):
            wagon.set_inventory_filter("incorrect", 0)

    def test_set_inventory_filters(self):
        wagon = CargoWagon("cargo-wagon")

        # Shorthand
        data = ["iron-ore", "copper-ore", "coal"]
        wagon.inventory_filters = data
        assert wagon.inventory_filters == [
            AttrsItemFilter(**{"index": 0, "name": "iron-ore"}),
            AttrsItemFilter(**{"index": 1, "name": "copper-ore"}),
            AttrsItemFilter(**{"index": 2, "name": "coal"}),
        ]

        # Longhand
        data = [
            {"index": 0, "name": "iron-ore"},
            {"index": 1, "name": "copper-ore"},
            {"index": 2, "name": "coal"},
        ]
        wagon.inventory_filters = data
        assert wagon.inventory_filters == [
            AttrsItemFilter(**{"index": 0, "name": "iron-ore"}),
            AttrsItemFilter(**{"index": 1, "name": "copper-ore"}),
            AttrsItemFilter(**{"index": 2, "name": "coal"}),
        ]

        with pytest.raises(DataFormatError):
            wagon.inventory_filters = "incorrect"

    def test_set_inventory_bar(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.bar == None
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
        }

        wagon.bar = 10
        assert wagon.bar == 10
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
            "inventory": {"bar": 10},
        }

        wagon.validate_assignment = ValidationMode.PEDANTIC
        with pytest.warns(BarWarning):
            wagon.bar = 100
        assert wagon.bar == 100

        with pytest.raises(DataFormatError):
            wagon.bar = "incorrect"
        assert wagon.bar == 100

        wagon.validate_assignment = "none"
        assert wagon.validate_assignment == ValidationMode.NONE

        wagon.bar = "incorrect"
        assert wagon.bar == "incorrect"
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
            "inventory": {"bar": "incorrect"},
        }

    def test_mergable_with(self):
        wagon1 = CargoWagon("cargo-wagon")
        wagon2 = CargoWagon(
            "cargo-wagon",
            tags={"some": "stuff"},
            bar=1,
            inventory_filters=[{"index": 1, "name": "transport-belt"}],
        )

        assert wagon1.mergable_with(wagon2)
        assert wagon2.mergable_with(wagon1)

        wagon2.tile_position = [-10, -10]
        assert not wagon1.mergable_with(wagon2)

        wagon2.tile_position = (0, 0)
        wagon2.orientation = 0.1
        assert not wagon1.mergable_with(wagon2)

    def test_merge(self):
        wagon1 = CargoWagon("cargo-wagon")
        wagon2 = CargoWagon(
            "cargo-wagon",
            tags={"some": "stuff"},
            bar=1,
            inventory_filters=[{"index": 1, "name": "transport-belt"}],
        )

        wagon1.merge(wagon2)
        del wagon2

        assert wagon1.tags == {"some": "stuff"}
        assert wagon1.bar == 1
        assert wagon1.inventory_filters == [
            AttrsItemFilter(**{"index": 1, "name": "transport-belt"})
        ]

    def test_eq(self):
        generator1 = CargoWagon("cargo-wagon")
        generator2 = CargoWagon("cargo-wagon")

        assert generator1 == generator2

        generator1.set_inventory_filter(5, "transport-belt")

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
