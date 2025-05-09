# test_elevated_curved_rail_a.py

from draftsman.prototypes.elevated_curved_rail_a import (
    ElevatedCurvedRailA,
    elevated_curved_rails_a,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    curved_rail = ElevatedCurvedRailA("elevated-curved-rail-a")

    with pytest.warns(UnknownEntityWarning):
        ElevatedCurvedRailA("unknown curved rail")


def test_flags():
    for rail_name in elevated_curved_rails_a:
        curved_rail = ElevatedCurvedRailA(rail_name)
        assert curved_rail.power_connectable == False
        assert curved_rail.dual_power_connectable == False
        assert curved_rail.circuit_connectable == False
        assert curved_rail.dual_circuit_connectable == False
