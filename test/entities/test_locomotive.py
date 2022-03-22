# test_locomotive.py

from draftsman.entity import Locomotive, locomotives
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

from unittest import TestCase

class LocomotiveTesting(TestCase):
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
        with self.assertWarns(DraftsmanWarning):
            Locomotive("locomotive", unused_keyword = "whatever")
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Locomotive("this is not a locomotive")
        with self.assertRaises(TypeError):
            Locomotive("locomotive", orientation = "wrong")
        with self.assertRaises(TypeError):
            Locomotive("locomotive", color = "also wrong")