# test_cargo_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import CargoWagon, cargo_wagons
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class CargoWagonTesting(TestCase):
    def test_constructor_init(self):
        cargo_wagon = CargoWagon(
            "cargo-wagon", tile_position=[0, 0], inventory={"bar": 0}
        )
        self.assertEqual(
            cargo_wagon.to_dict(),
            {
                "name": "cargo-wagon",
                "position": {"x": 1.0, "y": 2.5},
                "inventory": {"bar": 0},
            },
        )

        cargo_wagon = CargoWagon(
            "cargo-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
            inventory={
                "bar": 10,
                "filters": ["transport-belt", "transport-belt", "transport-belt"],
            },
        )
        self.assertEqual(
            cargo_wagon.to_dict(),
            {
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
            },
        )

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
        self.assertEqual(
            cargo_wagon.to_dict(),
            {
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
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            CargoWagon("cargo-wagon", unused_keyword="whatever")
        # Warn if the cargo wagon is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with self.assertRaises(InvalidEntityError):
            CargoWagon("this is not a cargo-wagon")
        with self.assertRaises(TypeError):
            CargoWagon("cargo-wagon", orientation="wrong")
        with self.assertRaises(DataFormatError):
            CargoWagon("cargo-wagon", inventory="incorrect")
