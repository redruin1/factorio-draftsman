# test_legacy_straight_rail.py

from draftsman.constants import Direction
from draftsman.prototypes.legacy_straight_rail import (
    LegacyStraightRail,
    legacy_straight_rails,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_legacy_straight_rail():
    if len(legacy_straight_rails) == 0:
        return None
    return LegacyStraightRail(
        "legacy-straight-rail",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


def test_constructor():
    straight_rail = LegacyStraightRail("legacy-straight-rail")

    with pytest.warns(UnknownEntityWarning):
        LegacyStraightRail("unknown display panel")


def test_flags():
    for rail_name in legacy_straight_rails:
        rail = LegacyStraightRail(rail_name)
        assert rail.power_connectable == False
        assert rail.dual_power_connectable == False
        assert rail.circuit_connectable == False
        assert rail.dual_circuit_connectable == False
