# test_elevated_half_diagonal_rail.py

from draftsman.constants import Direction
from draftsman.prototypes.elevated_half_diagonal_rail import (
    ElevatedHalfDiagonalRail,
    elevated_half_diagonal_rails,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_elevated_half_diagonal_rail():
    if len(elevated_half_diagonal_rails) == 0:
        return None
    return ElevatedHalfDiagonalRail(
        "elevated-half-diagonal-rail",
        id="test",
        quality="uncommon",
        tile_position=(2, 2),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(
    len(elevated_half_diagonal_rails) == 0,
    reason="No ElevatedHalfDiagonalRails to test",
)
class TestElevatedHalfDiagonalRail:
    def test_constructor(self):
        diagonal_rail = ElevatedHalfDiagonalRail("elevated-half-diagonal-rail")

        with pytest.warns(UnknownEntityWarning):
            ElevatedHalfDiagonalRail("unknown diagonal rail")

    def test_flags(self):
        for rail_name in elevated_half_diagonal_rails:
            rail = ElevatedHalfDiagonalRail(rail_name)
            assert rail.double_grid_aligned == True
            assert rail.power_connectable == False
            assert rail.dual_power_connectable == False
            assert rail.circuit_connectable == False
            assert rail.dual_circuit_connectable == False
