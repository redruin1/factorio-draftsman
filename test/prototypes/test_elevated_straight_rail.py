# test_elevated_straight_rail.py

from draftsman.prototypes.elevated_straight_rail import (
    ElevatedStraightRail,
    elevated_straight_rails,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    rail = ElevatedStraightRail("elevated-straight-rail")

    with pytest.warns(UnknownEntityWarning):
        ElevatedStraightRail("unknown elevated straight rail")


def test_flags():
    for rail_name in elevated_straight_rails:
        print(rail_name)
        rail = ElevatedStraightRail(rail_name)
        assert rail.power_connectable == False
        assert rail.dual_power_connectable == False
        assert rail.circuit_connectable == False
        assert rail.dual_circuit_connectable == False
