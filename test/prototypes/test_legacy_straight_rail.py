# test_legacy_straight_rail.py

from draftsman.constants import Direction, LegacyDirection
from draftsman.prototypes.legacy_straight_rail import (
    LegacyStraightRail,
    legacy_straight_rails,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_legacy_straight_rail():
    return LegacyStraightRail(
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


class TestLegacyStraightRail:
    def test_constructor(self):
        straight_rail = LegacyStraightRail(direction=Direction.NORTHWEST)
        assert straight_rail.to_dict(version=(1, 0)) == {
            "name": "straight-rail",
            "position": {"x": 1, "y": 1},
            "direction": LegacyDirection.NORTHWEST,
        }
        assert straight_rail.to_dict(version=(2, 0)) == {
            "name": "legacy-straight-rail",
            "position": {"x": 1, "y": 1},
            "direction": Direction.NORTHWEST,
        }

        with pytest.warns(UnknownEntityWarning):
            LegacyStraightRail("unknown legacy straight rail")

    def test_flags(self):
        for rail_name in legacy_straight_rails:
            rail = LegacyStraightRail(rail_name)
            assert rail.double_grid_aligned == True
            assert rail.power_connectable == False
            assert rail.dual_power_connectable == False
            assert rail.circuit_connectable == False
            assert rail.dual_circuit_connectable == False
