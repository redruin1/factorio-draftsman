# test_curved_rail.py

from draftsman.constants import Direction
from draftsman.entity import CurvedRail, curved_rails, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import GridAlignmentWarning, UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestCurvedRail:
    def test_constructor_init(self):
        curved_rail = CurvedRail(
            "curved-rail", tile_position=[0, 0], direction=Direction.NORTHWEST
        )
        print(curved_rail.tile_width, curved_rail.tile_height)
        print(curved_rail.collision_set)
        assert curved_rail.to_dict() == {
            "name": "curved-rail",
            "position": {"x": 4.0, "y": 2.5},
            "direction": 7,
        }

        # Warnings:
        with pytest.warns(UnknownKeywordWarning):
            CurvedRail("curved-rail", invalid_keyword="whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with pytest.warns(GridAlignmentWarning):
            CurvedRail("curved-rail", tile_position=[1, 1])
        with pytest.warns(UnknownEntityWarning):
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
