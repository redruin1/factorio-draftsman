# test_half_diagonal_rail.py

from draftsman.prototypes.half_diagonal_rail import (
    HalfDiagonalRail,
    half_diagonal_rails,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    rail = HalfDiagonalRail("half-diagonal-rail")

    with pytest.warns(UnknownEntityWarning):
        HalfDiagonalRail("unknown diagonal rail")


def test_flags():
    for rail_name in half_diagonal_rails:
        rail = HalfDiagonalRail(rail_name)
        assert rail.power_connectable == False
        assert rail.dual_power_connectable == False
        assert rail.circuit_connectable == False
        assert rail.dual_circuit_connectable == False