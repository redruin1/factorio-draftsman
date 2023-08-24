# test_curved_rail.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import CurvedRail, curved_rails, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning, RailAlignmentWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class CurvedRailTesting(unittest.TestCase):
    def test_constructor_init(self):
        curved_rail = CurvedRail(
            "curved-rail", tile_position=[0, 0], direction=Direction.NORTHWEST
        )
        assert curved_rail.to_dict() == {
            "name": "curved-rail",
            "position": {"x": 4.0, "y": 2.5},
            "direction": 7,
        }

        # Warnings:
        with pytest.warns(DraftsmanWarning):
            CurvedRail("curved-rail", invalid_keyword="whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with pytest.warns(RailAlignmentWarning):
            CurvedRail("curved-rail", tile_position=[1, 1])

        # Errors
        with pytest.raises(InvalidEntityError):
            CurvedRail("this is not a curved rail")

    def test_mergable_with(self):
        rail1 = CurvedRail("curved-rail")
        rail2 = CurvedRail("curved-rail", tags={"some": "stuff"})

        assert rail1.mergable_with(rail2)
        assert rail2.mergable_with(rail1)

        rail2.direction = Direction.NORTHEAST
        assert not rail1.mergable_with(rail2)

        rail2.direction = Direction.NORTH
        rail2.tile_position = (10, 10)
        assert not rail1.mergable_with(rail2)

    def test_merge(self):
        rail1 = CurvedRail("curved-rail")
        rail2 = CurvedRail("curved-rail", tags={"some": "stuff"})

        rail1.merge(rail2)
        del rail2

        assert rail1.tags == {"some": "stuff"}

    def test_eq(self):
        generator1 = CurvedRail("curved-rail")
        generator2 = CurvedRail("curved-rail")

        assert generator1 == generator2

        generator1.tags = {"some": "stuff"}

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
