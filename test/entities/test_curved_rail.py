# test_curved_rail.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import CurvedRail, curved_rails
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning, RailAlignmentWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class CurvedRailTesting(unittest.TestCase):
    def test_constructor_init(self):
        curved_rail = CurvedRail(
            "curved-rail", tile_position=[0, 0], direction=Direction.NORTHWEST
        )
        self.assertEqual(
            curved_rail.to_dict(),
            {"name": "curved-rail", "position": {"x": 4.0, "y": 2.5}, "direction": 7},
        )

        # Warnings:
        with self.assertWarns(DraftsmanWarning):
            CurvedRail("curved-rail", invalid_keyword="whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with self.assertWarns(RailAlignmentWarning):
            CurvedRail("curved-rail", tile_position=[1, 1])

        # Errors
        with self.assertRaises(InvalidEntityError):
            CurvedRail("this is not a curved rail")

    def test_mergable_with(self):
        rail1 = CurvedRail("curved-rail")
        rail2 = CurvedRail("curved-rail", tags={"some": "stuff"})

        self.assertTrue(rail1.mergable_with(rail2))
        self.assertTrue(rail2.mergable_with(rail1))

        rail2.direction = Direction.NORTHEAST
        self.assertFalse(rail1.mergable_with(rail2))

        rail2.direction = Direction.NORTH
        rail2.tile_position = (10, 10)
        self.assertFalse(rail1.mergable_with(rail2))

    def test_merge(self):
        rail1 = CurvedRail("curved-rail")
        rail2 = CurvedRail("curved-rail", tags={"some": "stuff"})

        rail1.merge(rail2)
        del rail2

        self.assertEqual(rail1.tags, {"some": "stuff"})
