# test_curved_rail_a.py

from draftsman.prototypes.curved_rail_a import (
    CurvedRailA,
    curved_rails_a,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    curved_rail = CurvedRailA("curved-rail-a")

    with pytest.warns(UnknownEntityWarning):
        CurvedRailA("unknown curved rail")


def test_flags():
    for rail_name in curved_rails_a:
        curved_rail = CurvedRailA(rail_name)
        assert curved_rail.power_connectable == False
        assert curved_rail.dual_power_connectable == False
        assert curved_rail.circuit_connectable == False
        assert curved_rail.dual_circuit_connectable == False
