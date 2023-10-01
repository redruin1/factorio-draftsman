# test_cargo_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import CargoWagon, cargo_wagons, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class CargoWagonTesting(unittest.TestCase):
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
        with pytest.warns(DraftsmanWarning):
            CargoWagon("cargo-wagon", unused_keyword="whatever")
        # Warn if the cargo wagon is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with pytest.raises(InvalidEntityError):
            CargoWagon("this is not a cargo-wagon")
        with pytest.raises(TypeError):
            CargoWagon("cargo-wagon", orientation="wrong")
        # TODO: move to validate
        # with pytest.raises(DataFormatError):
        #     CargoWagon("cargo-wagon", inventory="incorrect")

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
        assert wagon1.inventory["filters"] == [{"index": 1, "name": "transport-belt"}]

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
