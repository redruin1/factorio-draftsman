# test_locomotive.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Locomotive, locomotives
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class LocomotiveTesting(TestCase):
    def test_constructor_init(self):
        locomotive = Locomotive(
            "locomotive",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
            color=[0.0, 1.0, 0.0],
        )
        self.assertEqual(
            locomotive.to_dict(),
            {
                "name": "locomotive",
                "position": {"x": 1.0, "y": 1.0},
                "orientation": 0.75,
                "color": {"r": 0.0, "g": 1.0, "b": 0.0},
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Locomotive("locomotive", unused_keyword="whatever")
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Locomotive("this is not a locomotive")
        with self.assertRaises(TypeError):
            Locomotive("locomotive", orientation="wrong")
        with self.assertRaises(DataFormatError):
            Locomotive("locomotive", color="also wrong")
