# test_lamp.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Lamp, lamps
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class LampTesting(TestCase):
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

    def test_set_use_colors(self):
        lamp = Lamp()
        lamp.use_colors = True
        self.assertEqual(lamp.control_behavior, {"use_colors": True})
        lamp.use_colors = None
        self.assertEqual(lamp.use_colors, None)
        self.assertEqual(lamp.control_behavior, {})
        with self.assertRaises(TypeError):
            lamp.use_colors = "incorrect"
