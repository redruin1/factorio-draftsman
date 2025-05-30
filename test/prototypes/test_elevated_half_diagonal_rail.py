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


def test_constructor():
    diagonal_rail = ElevatedHalfDiagonalRail("elevated-half-diagonal-rail")

    with pytest.warns(UnknownEntityWarning):
        ElevatedHalfDiagonalRail("unknown diagonal rail")


def test_flags():
    for rail_name in elevated_half_diagonal_rails:
        diagonal_rail = ElevatedHalfDiagonalRail(rail_name)
        assert diagonal_rail.power_connectable == False
        assert diagonal_rail.dual_power_connectable == False
        assert diagonal_rail.circuit_connectable == False
        assert diagonal_rail.dual_circuit_connectable == False
