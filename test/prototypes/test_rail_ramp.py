# test_rail_ramp.py

from draftsman.prototypes.rail_ramp import (
    RailRamp,
    rail_ramps,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    ramp = RailRamp("rail-ramp")

    with pytest.warns(UnknownEntityWarning):
        RailRamp("unknown rail ramp")


def test_flags():
    for ramp_name in rail_ramps:
        ramp = RailRamp(ramp_name)
        assert ramp.power_connectable == False
        assert ramp.dual_power_connectable == False
        assert ramp.circuit_connectable == False
        assert ramp.dual_circuit_connectable == False