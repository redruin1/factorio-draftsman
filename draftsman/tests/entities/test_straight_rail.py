# test_straight_rail.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import StraightRail, straight_rails
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning, RailAlignmentWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class StraightRailTesting(TestCase):  # Hoo boy
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
