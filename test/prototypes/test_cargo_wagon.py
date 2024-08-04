# test_cargo_wagon.py

from draftsman.constants import Orientation, ValidationMode
from draftsman.entity import CargoWagon, cargo_wagons, Container
from draftsman.error import DataFormatError
from draftsman.signatures import FilterEntry
from draftsman.warning import (
    BarWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest
import warnings


class TestCargoWagon:
    def test_constructor_init(self):
        cargo_wagon = CargoWagon(
            "cargo-wagon", tile_position=[0, 0], inventory={"bar": 0}
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
            inventory={
                "bar": 10,
                "filters": ["transport-belt", "transport-belt", "transport-belt"],
            },
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
            inventory={
                "bar": 10,
                "filters": [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "transport-belt"},
                    {"index": 3, "name": "transport-belt"},
                ],
            },
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
        with pytest.warns(UnknownKeywordWarning):
            CargoWagon("cargo-wagon", unused_keyword="whatever").validate().reissue_all()
        # Warn if the cargo wagon is not on a rail (close enough to one?)
        # TODO (Complex)
        with pytest.warns(UnknownEntityWarning):
            CargoWagon("this is not a cargo-wagon").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            CargoWagon("cargo-wagon", orientation="wrong").validate().reissue_all()
        with pytest.raises(DataFormatError):
            CargoWagon("cargo-wagon", inventory="incorrect").validate().reissue_all()

    def test_set_orientation(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.orientation == Orientation.NORTH
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
        }

        wagon.orientation = None
        assert wagon.orientation == Orientation.NORTH
        assert wagon.collision_set.shapes[0].angle == 0
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
        }

        # Unknown wagon
        wagon = CargoWagon("unknown-cargo-wagon", validate=ValidationMode.MINIMUM)
        wagon.orientation = None
        assert wagon.orientation == Orientation.NORTH
        assert wagon.collision_set is None
        assert wagon.to_dict() == {
            "name": "unknown-cargo-wagon",
            "position": {"x": 0.0, "y": 0.0},
        }

    def test_set_inventory(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.inventory == CargoWagon.Format.InventoryFilters()

        wagon.inventory = {"filters": None, "bar": 10}
        assert wagon.inventory == CargoWagon.Format.InventoryFilters(
            filters=None, bar=10
        )
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
            "inventory": {"bar": 10},
        }

    def test_set_filters(self):
        wagon = CargoWagon("cargo-wagon")
        assert wagon.filters == None
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
        }

        # Shorthand format
        wagon.filters = ["iron-ore", "copper-ore", "iron-ore"]
        assert wagon.filters == [
            FilterEntry(**{"index": 1, "name": "iron-ore"}),
            FilterEntry(**{"index": 2, "name": "copper-ore"}),
            FilterEntry(**{"index": 3, "name": "iron-ore"}),
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
        wagon.filters = [
            {"index": 1, "name": "iron-ore"},
            {"index": 2, "name": "copper-ore"},
            {"index": 3, "name": "iron-ore"},
        ]
        assert wagon.filters == [
            FilterEntry(**{"index": 1, "name": "iron-ore"}),
            FilterEntry(**{"index": 2, "name": "copper-ore"}),
            FilterEntry(**{"index": 3, "name": "iron-ore"}),
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
            wagon.filters = ["unknown"]
        assert wagon.filters == [
            FilterEntry(**{"index": 1, "name": "unknown"}),
        ]

        with pytest.raises(DataFormatError):
            wagon.filters = "incorrect"
        assert wagon.filters == [
            FilterEntry(**{"index": 1, "name": "unknown"}),
        ]

        wagon.validate_assignment = "none"
        assert wagon.validate_assignment == ValidationMode.NONE

        wagon.filters = "incorrect"
        assert wagon.filters == "incorrect"
        assert wagon.to_dict() == {
            "name": "cargo-wagon",
            "position": {"x": 1.0, "y": 2.5},
            "inventory": {"filters": "incorrect"},
        }

    def test_set_inventory_filter(self):
        wagon = CargoWagon("cargo-wagon")

        wagon.set_inventory_filter(0, "wooden-chest")
        assert wagon.filters == [
            FilterEntry(**{"index": 1, "name": "wooden-chest"}),
        ]

        # Replace existing
        wagon.set_inventory_filter(0, "iron-chest")
        assert wagon.filters == [
            FilterEntry(**{"index": 1, "name": "iron-chest"}),
        ]

        # Remove existing
        wagon.set_inventory_filter(0, None)
        assert wagon.filters == []

        # Ensure errors even if validation is off
        wagon.validate_assignment = "none"
        assert wagon.validate_assignment == ValidationMode.NONE
        with pytest.raises(DataFormatError):
            wagon.set_inventory_filter("incorrect", 0)

    def test_set_inventory_filters(self):
        wagon = CargoWagon("cargo-wagon")

        # Shorthand
        data = ["iron-ore", "copper-ore", "coal"]
        wagon.set_inventory_filters(data)
        assert wagon.filters == [
            FilterEntry(**{"index": 1, "name": "iron-ore"}),
            FilterEntry(**{"index": 2, "name": "copper-ore"}),
            FilterEntry(**{"index": 3, "name": "coal"}),
        ]

        # Longhand
        data = [
            {"index": 1, "name": "iron-ore"},
            {"index": 2, "name": "copper-ore"},
            {"index": 3, "name": "coal"},
        ]
        wagon.set_inventory_filters(data)
        assert wagon.filters == [
            FilterEntry(**{"index": 1, "name": "iron-ore"}),
            FilterEntry(**{"index": 2, "name": "copper-ore"}),
            FilterEntry(**{"index": 3, "name": "coal"}),
        ]

        wagon.set_inventory_filters(None)
        assert wagon.filters == None

        # Ensure errors even if validation is off
        wagon.validate_assignment = "none"
        assert wagon.validate_assignment == ValidationMode.NONE
        with pytest.raises(DataFormatError):
            wagon.set_inventory_filters("incorrect")

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

        wagon.bar = 100
        assert wagon.bar == 100

        wagon.validate_assignment = "minimum"
        assert wagon.validate_assignment == ValidationMode.MINIMUM
        with warnings.catch_warnings(record=True) as w:
            wagon.bar = 100
            assert len(w) == 0

        wagon.validate_assignment = ValidationMode.PEDANTIC
        with pytest.warns(BarWarning):
            wagon.bar = 100

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
            inventory={"bar": 1, "filters": [{"index": 1, "name": "transport-belt"}]},
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
            inventory={"bar": 1, "filters": [{"index": 1, "name": "transport-belt"}]},
        )

        wagon1.merge(wagon2)
        del wagon2

        assert wagon1.tags == {"some": "stuff"}
        assert wagon1.bar == 1
        assert wagon1.inventory["filters"] == [
            FilterEntry(**{"index": 1, "name": "transport-belt"})
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
