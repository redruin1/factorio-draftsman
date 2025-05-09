# test_elevated_curved_rail_b.py

from draftsman.prototypes.elevated_curved_rail_b import (
    ElevatedCurvedRailB,
    elevated_curved_rails_b,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    curved_rail = ElevatedCurvedRailB("elevated-curved-rail-b")

    with pytest.warns(UnknownEntityWarning):
        ElevatedCurvedRailB("unknown curved rail")


def test_flags():
    for rail_name in elevated_curved_rails_b:
        curved_rail = ElevatedCurvedRailB(rail_name)
        assert curved_rail.power_connectable == False
        assert curved_rail.dual_power_connectable == False
        assert curved_rail.circuit_connectable == False
        assert curved_rail.dual_circuit_connectable == False
