# test_fluid_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import FluidWagon, fluid_wagons
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class FluidWagonTesting(unittest.TestCase):
    def test_constructor_init(self):
        fluid_wagon = FluidWagon(
            "fluid-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
        )
        self.assertEqual(
            fluid_wagon.to_dict(),
            {
                "name": "fluid-wagon",
                "position": {"x": 1.0, "y": 1.0},
                "orientation": 0.75,
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            FluidWagon("fluid-wagon", unused_keyword="whatever")
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with self.assertRaises(InvalidEntityError):
            FluidWagon("this is not a fluid wagon")
        with self.assertRaises(TypeError):
            FluidWagon("fluid-wagon", orientation="wrong")

    def test_mergable_with(self):
        wagon1 = FluidWagon("fluid-wagon")
        wagon2 = FluidWagon("fluid-wagon", tags={"some": "stuff"})

        self.assertTrue(wagon1.mergable_with(wagon1))

        self.assertTrue(wagon1.mergable_with(wagon2))
        self.assertTrue(wagon2.mergable_with(wagon1))

        wagon2.orientation = 0.5
        self.assertFalse(wagon1.mergable_with(wagon2))

    def test_merge(self):
        wagon1 = FluidWagon("fluid-wagon")
        wagon2 = FluidWagon("fluid-wagon", tags={"some": "stuff"})

        wagon1.merge(wagon2)
        del wagon2

        self.assertEqual(wagon1.tags, {"some": "stuff"})
