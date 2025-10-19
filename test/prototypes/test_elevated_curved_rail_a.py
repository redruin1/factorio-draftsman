# test_elevated_curved_rail_a.py

from draftsman.constants import Direction
from draftsman.prototypes.elevated_curved_rail_a import (
    ElevatedCurvedRailA,
    elevated_curved_rails_a,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_elevated_curved_rail_a():
    if len(elevated_curved_rails_a) == 0:
        return None
    return ElevatedCurvedRailA(
        "elevated-curved-rail-a",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(
    len(elevated_curved_rails_a) == 0, reason="No ElevatedCurvedRailAs to test"
)
class TestElevatedCurvedRailA:
    def test_constructor(self):
        curved_rail = ElevatedCurvedRailA("elevated-curved-rail-a")

        with pytest.warns(UnknownEntityWarning):
            ElevatedCurvedRailA("unknown curved rail")

    def test_flags(self):
        for rail_name in elevated_curved_rails_a:
            rail = ElevatedCurvedRailA(rail_name)
            assert rail.double_grid_aligned == True
            assert rail.power_connectable == False
            assert rail.dual_power_connectable == False
            assert rail.circuit_connectable == False
            assert rail.dual_circuit_connectable == False
