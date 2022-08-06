# test_locomotive.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Locomotive, locomotives
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LocomotiveTesting(unittest.TestCase):
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

    def test_mergable_with(self):
        train1 = Locomotive("locomotive")
        train2 = Locomotive("locomotive", color=(100, 100, 100), tags={"some": "stuff"})

        self.assertTrue(train1.mergable_with(train1))

        self.assertTrue(train1.mergable_with(train2))
        self.assertTrue(train2.mergable_with(train1))

        train2.orientation = 0.5
        self.assertFalse(train1.mergable_with(train2))

    def test_merge(self):
        train1 = Locomotive("locomotive")
        train2 = Locomotive("locomotive", color=(100, 100, 100), tags={"some": "stuff"})

        train1.merge(train2)
        del train2

        self.assertEqual(train1.color, {"r": 100, "g": 100, "b": 100})
        self.assertEqual(train1.tags, {"some": "stuff"})
