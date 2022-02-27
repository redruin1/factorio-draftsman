# test_cargo_wagon.py

from draftsman.entity import CargoWagon, cargo_wagons
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class CargoWagonTesting(TestCase):
    def test_default_constructor(self):
        cargo_wagon = CargoWagon()
        self.assertEqual(
            cargo_wagon.to_dict(),
            {
                "name": "cargo-wagon",
                "position": {"x": 1.0, "y": 3.0}
            }
        )

    def test_constructor_init(self):
        cargo_wagon = CargoWagon(
            "cargo-wagon",
            position = [0, 0],
            inventory = {
                "bar": 0
            }
        )
        self.assertEqual(
            cargo_wagon.to_dict(),
            {
                "name": "cargo-wagon",
                "position": {"x": 1.0, "y": 3.0},
                "inventory": {
                    "bar": 0
                }
            }
        )

        cargo_wagon = CargoWagon(
            "cargo-wagon",
            position = {"x": 1.0, "y": 1.0},
            orientation = 0.75,
            inventory = {
                "bar": 10,
                "filters": ["transport-belt", "transport-belt", "transport-belt"]
            }
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
                    ]
                }
            }
        )

        cargo_wagon = CargoWagon(
            "cargo-wagon",
            position = {"x": 1.0, "y": 1.0},
            orientation = 0.75,
            inventory = {
                "bar": 10,
                "filters": [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "transport-belt"},
                    {"index": 3, "name": "transport-belt"},
                ]
            }
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
                    ]
                }
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            CargoWagon("cargo-wagon", unused_keyword = "whatever")
        # Warn if the cargo wagon is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with self.assertRaises(InvalidEntityID):
            CargoWagon("this is not a cargo-wagon")
        with self.assertRaises(SchemaError):
            CargoWagon("cargo-wagon", orientation = "wrong")
        with self.assertRaises(SchemaError):
            CargoWagon("cargo-wagon", inventory = "incorrect")

    def test_dimensions(self):
        for name in cargo_wagons:
            cargo_wagon = CargoWagon(name)
            self.assertEqual(cargo_wagon.width, 2)
            self.assertEqual(cargo_wagon.height, 6)
