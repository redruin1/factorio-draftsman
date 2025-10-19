# test_legacy_curved_rail.py

from draftsman.constants import Direction, LegacyDirection
from draftsman.entity import LegacyCurvedRail, Container
from draftsman.warning import (
    GridAlignmentWarning,
    UnknownEntityWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_legacy_curved_rail():
    return LegacyCurvedRail(
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


class TestLegacyCurvedRail:
    def test_constructor_init(self):
        curved_rail = LegacyCurvedRail(
            tile_position=(0, 0), direction=Direction.NORTHWEST
        )
        assert curved_rail.to_dict(version=(1, 0)) == {
            "name": "curved-rail",
            "position": {"x": 4.0, "y": 2.0},
            "direction": LegacyDirection.NORTHWEST,
        }
        assert curved_rail.to_dict(version=(2, 0)) == {
            "name": "legacy-curved-rail",
            "position": {"x": 4.0, "y": 2.0},
            "direction": Direction.NORTHWEST,
        }

        # Warnings:
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        # with pytest.warns(GridAlignmentWarning):
        #     LegacyCurvedRail(tile_position=(1, 1))
        with pytest.warns(UnknownEntityWarning):
            LegacyCurvedRail("this is not a curved rail")

    def test_flags(self):
        rail = LegacyCurvedRail()
        assert rail.rotatable == True
        assert rail.square == False
        assert rail.double_grid_aligned == True

    def test_mergable_with(self):
        rail1 = LegacyCurvedRail()
        rail2 = LegacyCurvedRail(tags={"some": "stuff"})

        assert rail1.mergable_with(rail2)
        assert rail2.mergable_with(rail1)

        rail2.direction = Direction.NORTHEAST
        assert not rail1.mergable_with(rail2)

        rail2.direction = Direction.NORTH
        rail2.tile_position = (10, 10)
        assert not rail1.mergable_with(rail2)

    def test_merge(self):
        rail1 = LegacyCurvedRail()
        rail2 = LegacyCurvedRail(tags={"some": "stuff"})

        rail1.merge(rail2)
        del rail2

        assert rail1.tags == {"some": "stuff"}

    def test_eq(self):
        generator1 = LegacyCurvedRail()
        generator2 = LegacyCurvedRail()

        assert generator1 == generator2

        generator1.tags = {"some": "stuff"}

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
