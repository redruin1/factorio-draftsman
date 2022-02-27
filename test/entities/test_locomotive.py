# test_locomotive.py

from draftsman.entity import Locomotive, locomotives
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class LocomotiveTesting(TestCase):
    def test_default_constructor(self):
        locomotive = Locomotive()
        self.assertEqual(
            locomotive.to_dict(),
            {
                "name": "locomotive",
                "position": {"x": 1.0, "y": 3.0}
            }
        )

    def test_constructor_init(self):
        locomotive = Locomotive(
            "locomotive",
            position = {"x": 1.0, "y": 1.0},
            orientation = 0.75,
            color = [0.0, 1.0, 0.0]
        )
        self.assertEqual(
            locomotive.to_dict(),
            {
                "name": "locomotive",
                "position": {"x": 1.0, "y": 1.0},
                "orientation": 0.75,
                "color": {"r": 0.0, "g": 1.0, "b": 0.0, "a": 1.0}
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            Locomotive("locomotive", unused_keyword = "whatever")
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with self.assertRaises(InvalidEntityID):
            Locomotive("this is not a locomotive")
        with self.assertRaises(SchemaError):
            Locomotive("locomotive", orientation = "wrong")
        with self.assertRaises(SchemaError):
            Locomotive("locomotive", color = "also wrong")

    def test_dimensions(self):
        for name in locomotives:
            locomotive = Locomotive(name)
            self.assertEqual(locomotive.width, 2)
            self.assertEqual(locomotive.height, 6)