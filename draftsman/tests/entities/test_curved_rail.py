# test_curved_rail.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import CurvedRail, curved_rails
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning, RailAlignmentWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class CurvedRailTesting(TestCase):
    def test_constructor_init(self):
        curved_rail = CurvedRail(
            "curved-rail", tile_position=[0, 0], direction=Direction.NORTHWEST
        )
        self.assertEqual(
            curved_rail.to_dict(),
            {"name": "curved-rail", "position": {"x": 2.0, "y": 2.0}, "direction": 7},
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
