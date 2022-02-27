# test_artillery_wagon.py

from draftsman.entity import ArtilleryWagon, artillery_wagons
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class ArtilleryWagonTesting(TestCase):
    def test_default_constructor(self):
        artillery_wagon = ArtilleryWagon()
        self.assertEqual(
            artillery_wagon.to_dict(),
            {
                "name": "artillery-wagon",
                "position": {"x": 1.0, "y": 3.0}
            }
        )

    def test_constructor_init(self):
        artillery_wagon = ArtilleryWagon(
            "artillery-wagon",
            position = {"x": 1.0, "y": 1.0},
            orientation = 0.75,
        )
        self.assertEqual(
            artillery_wagon.to_dict(),
            {
                "name": "artillery-wagon",
                "position": {"x": 1.0, "y": 1.0},
                "orientation": 0.75,
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            ArtilleryWagon("artillery-wagon", unused_keyword = "whatever")
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with self.assertRaises(InvalidEntityID):
            ArtilleryWagon("this is not an artillery wagon")
        with self.assertRaises(SchemaError):
            ArtilleryWagon("artillery-wagon", orientation = "wrong")

    def test_dimensions(self):
        for name in artillery_wagons:
            artillery_wagon = ArtilleryWagon(name)
            self.assertEqual(artillery_wagon.width, 2)
            self.assertEqual(artillery_wagon.height, 6)