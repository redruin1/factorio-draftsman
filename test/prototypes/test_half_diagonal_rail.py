# test_half_diagonal_rail.py

from draftsman.constants import Direction
from draftsman.prototypes.half_diagonal_rail import (
    HalfDiagonalRail,
    half_diagonal_rails,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_half_diagonal_rail():
    if len(half_diagonal_rails) == 0:
        return None
    return HalfDiagonalRail(
        "half-diagonal-rail",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(
    len(half_diagonal_rails) == 0, reason="No HalfDiagonalRails to test"
)
class TestHalfDiagonalRail:
    def test_constructor(self):
        rail = HalfDiagonalRail("half-diagonal-rail")

        with pytest.warns(UnknownEntityWarning):
            HalfDiagonalRail("unknown diagonal rail")

    def test_flags(self):
        for rail_name in half_diagonal_rails:
            rail = HalfDiagonalRail(rail_name)
            assert rail.power_connectable == False
            assert rail.dual_power_connectable == False
            assert rail.circuit_connectable == False
            assert rail.dual_circuit_connectable == False
