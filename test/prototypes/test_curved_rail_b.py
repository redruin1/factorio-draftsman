# test_curved_rail_b.py

from draftsman.constants import Direction
from draftsman.prototypes.curved_rail_b import (
    CurvedRailB,
    curved_rails_b,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_curved_rail_b():
    if len(curved_rails_b) == 0:
        return None
    return CurvedRailB(
        "curved-rail-b",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(len(curved_rails_b) == 0, reason="No CurvedRailBs to test")
class TestCurvedRailB:
    def test_constructor(self):
        curved_rail = CurvedRailB("curved-rail-b")

        with pytest.warns(UnknownEntityWarning):
            CurvedRailB("unknown curved rail")

    def test_flags(self):
        for rail_name in curved_rails_b:
            rail = CurvedRailB(rail_name)
            assert rail.double_grid_aligned == True
            assert rail.power_connectable == False
            assert rail.dual_power_connectable == False
            assert rail.circuit_connectable == False
            assert rail.dual_circuit_connectable == False
