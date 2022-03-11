# test_infinity_pipe.py

from draftsman.entity import InfinityPipe, infinity_pipes
from draftsman.error import (
    InvalidEntityError, InvalidFluidError, InvalidModeError
)
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

from unittest import TestCase

class InfinityPipeTesting(TestCase):
    def test_constructor_init(self):
        pipe = InfinityPipe(
            infinity_settings = {
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500
            }
        )
        self.assertEqual(
            pipe.to_dict(),
            {
                "name": "infinity-pipe",
                "position": {"x": 0.5, "y": 0.5},
                "infinity_settings": {
                    "name": "steam",
                    "percentage": 100,
                    "mode": "at-least",
                    "temperature": 500
                }
            }
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            InfinityPipe(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            InfinityPipe("this is not an infinity pipe")
        with self.assertRaises(SchemaError):
            InfinityPipe(
                infinity_settings = {
                    "clearly": "wrong"
                }
            )

    def test_set_infinity_settings(self):
        pipe = InfinityPipe()
        pipe.set_infinity_settings({
            "name": "steam",
            "percentage": 100,
            "mode": "at-least",
            "temperature": 500
        })
        self.assertEqual(
            pipe.infinity_settings,
            {
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500
            }
        )
        pipe.set_infinity_settings(None)
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(SchemaError):
            InfinityPipe(
                infinity_settings = {
                    "clearly": "wrong"
                }
            )

    def test_set_infinite_fluid_settings(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid("steam", 100, "at-least", 500)
        self.assertEqual(
            pipe.infinity_settings,
            {
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500
            }
        )
        with self.assertRaises(SchemaError):
            pipe.set_infinite_fluid(SchemaError)
        with self.assertRaises(InvalidFluidError):
            pipe.set_infinite_fluid("incorrect")
        with self.assertRaises(SchemaError):
            pipe.set_infinite_fluid("steam", "incorrect")
        with self.assertRaises(SchemaError):
            pipe.set_infinite_fluid("steam", 100, SchemaError)
        with self.assertRaises(InvalidModeError):
            pipe.set_infinite_fluid("steam", 100, "incorrect")
        with self.assertRaises(SchemaError):
            pipe.set_infinite_fluid("steam", 100, "at-least", "incorrect")

    def test_set_infinite_fluid_name(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid_name("steam")
        self.assertEqual(
            pipe.infinity_settings,
            {
                "name": "steam"
            }
        )
        pipe.set_infinite_fluid_name(None)
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(SchemaError):
            pipe.set_infinite_fluid_name(SchemaError)
        with self.assertRaises(InvalidFluidError):
            pipe.set_infinite_fluid_name("incorrect")

    def test_set_infinite_fluid_percentage(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid_percentage(50)
        self.assertEqual(
            pipe.infinity_settings,
            {
                "percentage": 50
            }
        )
        pipe.set_infinite_fluid_percentage(None)
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(SchemaError):
            pipe.set_infinite_fluid_percentage(SchemaError)

    def test_set_infinite_fluid_mode(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid_mode("at-most")
        self.assertEqual(
            pipe.infinity_settings,
            {
                "mode": "at-most"
            }
        )
        pipe.set_infinite_fluid_mode(None)
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(SchemaError):
            pipe.set_infinite_fluid_mode(SchemaError)
        with self.assertRaises(InvalidModeError):
            pipe.set_infinite_fluid_mode("incorrect")

    def test_set_infinite_fluid_temperature(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid_temperature(100)
        self.assertEqual(
            pipe.infinity_settings,
            {
                "temperature": 100
            }
        )
        pipe.set_infinite_fluid_temperature(None)
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(SchemaError):
            pipe.set_infinite_fluid_temperature(SchemaError)