# test_elevated_curved_rail_b.py

from draftsman.constants import Direction
from draftsman.prototypes.elevated_curved_rail_b import (
    ElevatedCurvedRailB,
    elevated_curved_rails_b,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_elevated_curved_rail_b():
    if len(elevated_curved_rails_b) == 0:
        return None
    return ElevatedCurvedRailB(
        "elevated-curved-rail-b",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(
    len(elevated_curved_rails_b) == 0, reason="No ElevatedCurvedRailBs to test"
)
class TestElevatedCurvedRailB:
    def test_constructor(self):
        curved_rail = ElevatedCurvedRailB("elevated-curved-rail-b")

        with pytest.warns(UnknownEntityWarning):
            ElevatedCurvedRailB("unknown curved rail")

    def test_flags(self):
        for rail_name in elevated_curved_rails_b:
            curved_rail = ElevatedCurvedRailB(rail_name)
            assert curved_rail.power_connectable == False
            assert curved_rail.dual_power_connectable == False
            assert curved_rail.circuit_connectable == False
            assert curved_rail.dual_circuit_connectable == False
