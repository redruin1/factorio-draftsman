# test_lamp.py

from draftsman.entity import Lamp, lamps
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class LampTesting(TestCase):
    def test_default_constructor(self):
        lamp = Lamp()
        self.assertEqual(
            lamp.to_dict(),
            {
                "name": "small-lamp",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        lamp = Lamp(
            "small-lamp",
            control_behavior = {
                "use_colors": True
            }
        )
        self.assertEqual(
            lamp.to_dict(),
            {
                "name": "small-lamp",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "use_colors": True
                }
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            Lamp("small-lamp", unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            Lamp("this is not a lamp")

    def test_dimensions(self):
        lamp = Lamp()
        self.assertEqual(lamp.tile_width, 1)
        self.assertEqual(lamp.tile_height, 1)

    def test_set_use_colors(self):
        lamp = Lamp()
        lamp.set_use_colors(True)
        self.assertEqual(
            lamp.control_behavior,
            {
                "use_colors": True
            }
        )
        lamp.set_use_colors(None)
        self.assertEqual(lamp.control_behavior, {})
        with self.assertRaises(SchemaError):
            lamp.set_use_colors("incorrect")