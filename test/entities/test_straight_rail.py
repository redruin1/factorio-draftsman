# test_straight_rail.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.entity import StraightRail, straight_rails
from draftsman.error import InvalidEntityError
from draftsman.warning import (
    DraftsmanWarning,
    RailAlignmentWarning,
    OverlappingObjectsWarning,
)

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class StraightRailTesting(unittest.TestCase):  # Hoo boy
    def test_constructor_init(self):
        straight_rail = StraightRail(
            "straight-rail", tile_position=[0, 0], direction=Direction.NORTHWEST
        )
        self.assertEqual(
            straight_rail.to_dict(),
            {"name": "straight-rail", "position": {"x": 1.0, "y": 1.0}, "direction": 7},
        )

        straight_rail = StraightRail(
            "straight-rail", position={"x": 101, "y": 101}, direction=Direction.SOUTH
        )
        self.assertEqual(
            straight_rail.to_dict(),
            {
                "name": "straight-rail",
                "position": {"x": 101.0, "y": 101.0},
                "direction": 4,
            },
        )

        # Warnings:
        with self.assertWarns(DraftsmanWarning):
            StraightRail("straight-rail", invalid_keyword="whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with self.assertWarns(RailAlignmentWarning):
            StraightRail("straight-rail", tile_position=[1, 1])

        # Errors
        with self.assertRaises(InvalidEntityError):
            StraightRail("this is not a straight rail")

    def test_overlapping(self):
        blueprint = Blueprint()
        blueprint.entities.append("straight-rail")
        # This shouldn't raise a warning
        blueprint.entities.append("straight-rail", direction=Direction.EAST)

        # But this should
        with self.assertWarns(OverlappingObjectsWarning):
            blueprint.entities.append("straight-rail")

    def test_mergable_with(self):
        rail1 = StraightRail("straight-rail")
        rail2 = StraightRail("straight-rail", tags={"some": "stuff"})

        self.assertTrue(rail1.mergable_with(rail1))

        self.assertTrue(rail1.mergable_with(rail2))
        self.assertTrue(rail2.mergable_with(rail1))

        rail2.tile_position = (2, 2)
        self.assertFalse(rail1.mergable_with(rail2))

    def test_merge(self):
        rail1 = StraightRail("straight-rail")
        rail2 = StraightRail("straight-rail", tags={"some": "stuff"})

        rail1.merge(rail2)
        del rail2

        self.assertEqual(rail1.tags, {"some": "stuff"})
