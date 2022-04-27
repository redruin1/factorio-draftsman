# test_infinity_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import InfinityPipe, infinity_pipes
from draftsman.error import InvalidEntityError, InvalidFluidError, InvalidModeError
from draftsman.warning import DraftsmanWarning, TemperatureRangeWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class InfinityPipeTesting(TestCase):
    def test_constructor_init(self):
        pipe = InfinityPipe(
            infinity_settings={
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500,
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
                    "temperature": 500,
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            InfinityPipe(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            InfinityPipe("this is not an infinity pipe")
        with self.assertRaises(TypeError):
            InfinityPipe(infinity_settings={"clearly": "wrong"})

    def test_set_infinity_settings(self):
        pipe = InfinityPipe()
        pipe.infinity_settings = {
            "name": "steam",
            "percentage": 100,
            "mode": "at-least",
            "temperature": 500,
        }
        self.assertEqual(
            pipe.infinity_settings,
            {
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500,
            },
        )
        pipe.infinity_settings = None
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(TypeError):
            InfinityPipe(infinity_settings={"clearly": "wrong"})

    def test_set_infinite_fluid_settings(self):
        pipe = InfinityPipe()
        pipe.set_infinite_fluid("steam", 100, "at-least", 500)
        self.assertEqual(
            pipe.infinity_settings,
            {
                "name": "steam",
                "percentage": 100,
                "mode": "at-least",
                "temperature": 500,
            },
        )

        with self.assertWarns(TemperatureRangeWarning):
            pipe.set_infinite_fluid("steam", 1, "at-least", -100)

        with self.assertRaises(TypeError):
            pipe.set_infinite_fluid(TypeError)
        with self.assertRaises(InvalidFluidError):
            pipe.set_infinite_fluid("incorrect")
        with self.assertRaises(TypeError):
            pipe.set_infinite_fluid("steam", "incorrect")
        with self.assertRaises(TypeError):
            pipe.set_infinite_fluid("steam", 1, SchemaError)
        with self.assertRaises(InvalidModeError):
            pipe.set_infinite_fluid("steam", 1, "incorrect")
        with self.assertRaises(TypeError):
            pipe.set_infinite_fluid("steam", 1, "at-least", "incorrect")
        with self.assertRaises(ValueError):
            pipe.set_infinite_fluid("steam", -1, "at-least")

    def test_set_infinite_fluid_name(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_name = "steam"
        self.assertEqual(pipe.infinite_fluid_name, "steam")
        self.assertEqual(pipe.infinity_settings, {"name": "steam"})
        pipe.infinite_fluid_name = None
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(TypeError):
            pipe.infinite_fluid_name = TypeError
        with self.assertRaises(InvalidFluidError):
            pipe.infinite_fluid_name = "incorrect"

    def test_set_infinite_fluid_percentage(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_percentage = 0.5
        self.assertEqual(pipe.infinite_fluid_percentage, 0.5)
        self.assertEqual(pipe.infinity_settings, {"percentage": 0.5})
        pipe.infinite_fluid_percentage = None
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(TypeError):
            pipe.infinite_fluid_percentage = TypeError
        with self.assertRaises(ValueError):
            pipe.infinite_fluid_percentage = -1

    def test_set_infinite_fluid_mode(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_mode = "at-most"
        self.assertEqual(pipe.infinite_fluid_mode, "at-most")
        self.assertEqual(pipe.infinity_settings, {"mode": "at-most"})
        pipe.infinite_fluid_mode = None
        self.assertEqual(pipe.infinity_settings, {})
        with self.assertRaises(TypeError):
            pipe.infinite_fluid_mode = TypeError
        with self.assertRaises(InvalidModeError):
            pipe.infinite_fluid_mode = "incorrect"

    def test_set_infinite_fluid_temperature(self):
        pipe = InfinityPipe()
        pipe.infinite_fluid_temperature = 100
        self.assertEqual(pipe.infinite_fluid_temperature, 100)
        self.assertEqual(pipe.infinity_settings, {"temperature": 100})
        pipe.infinite_fluid_temperature = None
        self.assertEqual(pipe.infinity_settings, {})

        with self.assertWarns(TemperatureRangeWarning):
            pipe.infinite_fluid_temperature = -100

        with self.assertRaises(TypeError):
            pipe.infinite_fluid_temperature = TypeError
