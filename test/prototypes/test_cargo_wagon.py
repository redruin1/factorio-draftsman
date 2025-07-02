# test_cargo_wagon.py

from draftsman.constants import InventoryType, Orientation, ValidationMode
from draftsman.entity import CargoWagon, cargo_wagons, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    Inventory,
    ItemFilter,
    BlueprintInsertPlan,
    ItemInventoryPositions,
    InventoryPosition,
    EquipmentComponent,
)
import draftsman.validators
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
    with draftsman.validators.set_mode(ValidationMode.MINIMUM):
        return CargoWagon(
            "cargo-wagon",
            id="test",
            quality="uncommon",
            tile_position=(1, 1),
            orientation=Orientation.EAST,
            inventory=Inventory(
                bar=10,
                filters=[ItemFilter(index=0, name="iron-ore")],
            ),
            item_requests=[
                BlueprintInsertPlan(
                    id="iron-ore",
                    items=ItemInventoryPositions(
                        in_inventory=[
                            InventoryPosition(
                                inventory=InventoryType.cargo_wagon, stack=0, count=50
                            )
                        ]
                    ),
                ),
                BlueprintInsertPlan(
                    id="energy-shield-equipment",
                    items=ItemInventoryPositions(grid_count=1),
                ),
            ],
            equipment=[
                EquipmentComponent(equipment="energy-shield-equipment", position=(0, 0))
            ],
            tags={"blah": "blah"},
        )


class TestCargoWagon:
    def test_constructor_init(self):
        cargo_wagon = CargoWagon(
            "cargo-wagon", tile_position=[0, 0], inventory=Inventory(bar=0)
        )
        assert cargo_wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 0.0, "y": 0.0},
            "inventory": {"bar": 0},
        }

        cargo_wagon = CargoWagon(
            "cargo-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
            inventory=Inventory(
                bar=10, filters=["transport-belt", "transport-belt", "transport-belt"]
            ),
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
            inventory=Inventory(
                bar=10,
                filters=[
                    ItemFilter(index=0, name="transport-belt"),
                    ItemFilter(index=1, name="transport-belt"),
                    ItemFilter(index=2, name="transport-belt"),
                ],
            ),
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
            "position": {"x": 0.0, "y": 0.0},
        }

        wagon.orientation = 0.0
        assert wagon.orientation == Orientation.NORTH
        assert wagon.collision_set.shapes[0].angle == 0
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 0.0, "y": 0.0},
        }

        # Unknown wagon
        with pytest.warns(UnknownEntityWarning):
            wagon = CargoWagon("unknown-cargo-wagon")
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

    def test_inventory_size(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.inventory.size == 40

        assert wagon.prototype.get("quality_affects_inventory_size", False) is False
        wagon.quality = "legendary"
        assert wagon.inventory.size == 40

        # Manually override to test the modded case
        wagon.prototype["quality_affects_inventory_size"] = True
        assert wagon.inventory.size == 100

        with pytest.warns(UnknownEntityWarning):
            wagon = CargoWagon("unknown wagon")
        assert wagon.inventory.size is None

    def test_set_inventory_filters(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.inventory.filters == []
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 0.0, "y": 0.0},
        }

        # Shorthand format
        wagon.inventory.filters = ["iron-ore", "copper-ore", "iron-ore"]
        assert wagon.inventory.filters == [
            ItemFilter(**{"index": 0, "name": "iron-ore"}),
            ItemFilter(**{"index": 1, "name": "copper-ore"}),
            ItemFilter(**{"index": 2, "name": "iron-ore"}),
        ]
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 0.0, "y": 0.0},
            "inventory": {
                "filters": [
                    {"index": 1, "name": "iron-ore"},
                    {"index": 2, "name": "copper-ore"},
                    {"index": 3, "name": "iron-ore"},
                ]
            },
        }

        # Explicit format
        wagon.inventory.filters = [
            {"index": 0, "name": "iron-ore"},
            {"index": 1, "name": "copper-ore"},
            {"index": 2, "name": "iron-ore"},
        ]
        assert wagon.inventory.filters == [
            ItemFilter(**{"index": 0, "name": "iron-ore"}),
            ItemFilter(**{"index": 1, "name": "copper-ore"}),
            ItemFilter(**{"index": 2, "name": "iron-ore"}),
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
            wagon.inventory.filters = ["unknown"]
            assert wagon.inventory.filters == [
                ItemFilter(**{"index": 0, "name": "unknown"}),
            ]

        with pytest.raises(DataFormatError):
            wagon.inventory.filters = "incorrect"
        assert wagon.inventory.filters[0].name == "unknown"

    def test_set_inventory_filter(self):
        wagon = CargoWagon("cargo-wagon")

        wagon.inventory.set_filter(0, "wooden-chest")
        assert wagon.inventory.filters == [
            ItemFilter(**{"index": 0, "name": "wooden-chest"}),
        ]

        # Replace existing
        wagon.inventory.set_filter(0, "iron-chest")
        assert wagon.inventory.filters == [
            ItemFilter(**{"index": 0, "name": "iron-chest"}),
        ]

        # Remove existing
        wagon.inventory.set_filter(0, None)
        assert wagon.inventory.filters == []

        # TODO: Ensure errors even if validation is off
        with pytest.raises(DataFormatError):
            wagon.inventory.set_filter("incorrect", 0)

    def test_set_inventory_filters(self):
        wagon = CargoWagon("cargo-wagon")

        # Shorthand
        data = ["iron-ore", "copper-ore", "coal"]
        wagon.inventory.filters = data
        assert wagon.inventory.filters == [
            ItemFilter(**{"index": 0, "name": "iron-ore"}),
            ItemFilter(**{"index": 1, "name": "copper-ore"}),
            ItemFilter(**{"index": 2, "name": "coal"}),
        ]

        with pytest.raises(DataFormatError):
            wagon.inventory.filters = "incorrect"

    def test_set_inventory_bar(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.inventory.bar == None
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 0.0, "y": 0.0},
        }

        wagon.inventory.bar = 10
        assert wagon.inventory.bar == 10
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 0.0, "y": 0.0},
            "inventory": {"bar": 10},
        }

        with draftsman.validators.set_mode(ValidationMode.PEDANTIC):
            with pytest.warns(BarWarning):
                wagon.inventory.bar = 100
            assert wagon.inventory.bar == 100

        with pytest.raises(DataFormatError):
            wagon.inventory.bar = "incorrect"
        assert wagon.inventory.bar == 100

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            wagon.inventory.bar = "incorrect"
            assert wagon.inventory.bar == "incorrect"
            assert wagon.to_dict() == {
                "name": "cargo-wagon",
                "position": {"x": 0.0, "y": 0.0},
                "inventory": {"bar": "incorrect"},
            }

    def test_mergable_with(self):
        wagon1 = CargoWagon("cargo-wagon")
        wagon2 = CargoWagon(
            "cargo-wagon",
            tags={"some": "stuff"},
            inventory=Inventory(
                bar=1, filters=[ItemFilter(index=1, name="transport-belt")]
            ),
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
            inventory=Inventory(
                bar=1, filters=[ItemFilter(index=1, name="transport-belt")]
            ),
        )

        wagon1.merge(wagon2)
        del wagon2

        assert wagon1.tags == {"some": "stuff"}
        assert wagon1.inventory.bar == 1
        assert wagon1.inventory.filters == [
            ItemFilter(**{"index": 1, "name": "transport-belt"})
        ]

    def test_eq(self):
        wagon1 = CargoWagon("cargo-wagon")
        wagon2 = CargoWagon("cargo-wagon")

        assert wagon1 == wagon2

        wagon1.inventory.set_filter(5, "transport-belt")

        assert wagon1 != wagon2

        container = Container()

        assert wagon1 != container
        assert wagon2 != container

        # hashable
        assert isinstance(wagon1, Hashable)
