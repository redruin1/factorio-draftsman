# test_rail_ramp.py

from draftsman.constants import Direction
from draftsman.prototypes.rail_ramp import (
    RailRamp,
    rail_ramps,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_rail_ramp():
    if len(rail_ramps) == 0:
        return None
    return RailRamp(
        "rail-ramp",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(len(rail_ramps) == 0, reason="No RailRamps to test")
class TestRailRamp:
    def test_constructor(self):
        ramp = RailRamp("rail-ramp")

        with pytest.warns(UnknownEntityWarning):
            RailRamp("unknown rail ramp")

    def test_flags(self):
        for ramp_name in rail_ramps:
            ramp = RailRamp(ramp_name)
            assert ramp.power_connectable == False
            assert ramp.dual_power_connectable == False
            assert ramp.circuit_connectable == False
            assert ramp.dual_circuit_connectable == False
