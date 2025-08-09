# test_elevated_straight_rail.py

from draftsman.constants import Direction
from draftsman.prototypes.elevated_straight_rail import (
    ElevatedStraightRail,
    elevated_straight_rails,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_elevated_straight_rail():
    if len(elevated_straight_rails) == 0:
        return None
    return ElevatedStraightRail(
        "elevated-straight-rail",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(
    len(elevated_straight_rails) == 0, reason="No ElevatedStraightRails to test"
)
class TestElevatedStraightRail:
    def test_constructor(self):
        rail = ElevatedStraightRail("elevated-straight-rail")

        with pytest.warns(UnknownEntityWarning):
            ElevatedStraightRail("unknown elevated straight rail")

    def test_flags(self):
        for rail_name in elevated_straight_rails:
            print(rail_name)
            rail = ElevatedStraightRail(rail_name)
            assert rail.power_connectable == False
            assert rail.dual_power_connectable == False
            assert rail.circuit_connectable == False
            assert rail.dual_circuit_connectable == False
