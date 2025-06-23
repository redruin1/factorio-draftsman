# test_legacy_curved_rail.py

from draftsman.constants import Direction
from draftsman.entity import LegacyCurvedRail, legacy_curved_rails, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import (
    GridAlignmentWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_legacy_curved_rail():
    if len(legacy_curved_rails) == 0:
        return None
    return LegacyCurvedRail(
        "legacy-curved-rail",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


class TestLegacyCurvedRail:
    def test_constructor_init(self):
        curved_rail = LegacyCurvedRail(
            "legacy-curved-rail", tile_position=(0, 0), direction=Direction.NORTHWEST
        )
        assert curved_rail.to_dict() == {
            "name": "legacy-curved-rail",
            "position": {"x": 4.0, "y": 2.0},
            "direction": Direction.NORTHWEST,
        }

        # Warnings:
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with pytest.warns(GridAlignmentWarning):
            LegacyCurvedRail(
                "legacy-curved-rail", tile_position=(1, 1)
            ).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            LegacyCurvedRail("this is not a curved rail").validate().reissue_all()

    def test_flags(self):
        rail = LegacyCurvedRail("legacy-curved-rail")
        assert rail.rotatable == True
        assert rail.square == False
        assert rail.double_grid_aligned == True

    def test_mergable_with(self):
        rail1 = LegacyCurvedRail("legacy-curved-rail")
        rail2 = LegacyCurvedRail("legacy-curved-rail", tags={"some": "stuff"})

        assert rail1.mergable_with(rail2)
        assert rail2.mergable_with(rail1)

        rail2.direction = Direction.NORTHEAST
        assert not rail1.mergable_with(rail2)

        rail2.direction = Direction.NORTH
        rail2.tile_position = (10, 10)
        assert not rail1.mergable_with(rail2)

    def test_merge(self):
        rail1 = LegacyCurvedRail("legacy-curved-rail")
        rail2 = LegacyCurvedRail("legacy-curved-rail", tags={"some": "stuff"})

        rail1.merge(rail2)
        del rail2

        assert rail1.tags == {"some": "stuff"}

    def test_eq(self):
        generator1 = LegacyCurvedRail("legacy-curved-rail")
        generator2 = LegacyCurvedRail("legacy-curved-rail")

        assert generator1 == generator2

        generator1.tags = {"some": "stuff"}

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
