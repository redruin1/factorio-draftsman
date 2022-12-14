# test_lamp.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Lamp, lamps
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LampTesting(unittest.TestCase):
    def test_constructor_init(self):
        lamp = Lamp("small-lamp", control_behavior={"use_colors": True})
        self.assertEqual(
            lamp.to_dict(),
            {
                "name": "small-lamp",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {"use_colors": True},
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Lamp("small-lamp", unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Lamp("this is not a lamp")
        with self.assertRaises(DataFormatError):
            Lamp(control_behavior={"unused_key": "something"})

    def test_set_use_colors(self):
        lamp = Lamp("small-lamp")
        lamp.use_colors = True
        self.assertEqual(lamp.control_behavior, {"use_colors": True})
        lamp.use_colors = None
        self.assertEqual(lamp.use_colors, None)
        self.assertEqual(lamp.control_behavior, {})
        with self.assertRaises(TypeError):
            lamp.use_colors = "incorrect"

    def test_mergable_with(self):
        lamp1 = Lamp("small-lamp")
        lamp2 = Lamp(
            "small-lamp", control_behavior={"use_colors": True}, tags={"some": "stuff"}
        )

        self.assertTrue(lamp1.mergable_with(lamp1))

        self.assertTrue(lamp1.mergable_with(lamp2))
        self.assertTrue(lamp2.mergable_with(lamp1))

        lamp2.tile_position = (1, 1)
        self.assertFalse(lamp1.mergable_with(lamp2))

    def test_merge(self):
        lamp1 = Lamp("small-lamp")
        lamp2 = Lamp(
            "small-lamp", control_behavior={"use_colors": True}, tags={"some": "stuff"}
        )

        lamp1.merge(lamp2)
        del lamp2

        self.assertEqual(lamp1.use_colors, True)
        self.assertEqual(lamp1.tags, {"some": "stuff"})
