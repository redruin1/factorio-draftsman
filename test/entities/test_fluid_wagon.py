# test_fluid_wagon.py

from draftsman.entity import FluidWagon, fluid_wagons
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class FluidWagonTesting(TestCase):
    def test_default_constructor(self):
        fluid_wagon = FluidWagon()
        self.assertEqual(
            fluid_wagon.to_dict(),
            {
                "name": "fluid-wagon",
                "position": {"x": 1.0, "y": 3.0}
            }
        )

    def test_constructor_init(self):
        fluid_wagon = FluidWagon(
            "fluid-wagon",
            position = {"x": 1.0, "y": 1.0},
            orientation = 0.75,
        )
        self.assertEqual(
            fluid_wagon.to_dict(),
            {
                "name": "fluid-wagon",
                "position": {"x": 1.0, "y": 1.0},
                "orientation": 0.75,
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            FluidWagon("fluid-wagon", unused_keyword = "whatever")
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with self.assertRaises(InvalidEntityID):
            FluidWagon("this is not a fluid wagon")
        with self.assertRaises(SchemaError):
            FluidWagon("fluid-wagon", orientation = "wrong")

    def test_dimensions(self):
        for name in fluid_wagons:
            fluid_wagon = FluidWagon(name)
            self.assertEqual(fluid_wagon.width, 2)
            self.assertEqual(fluid_wagon.height, 6)