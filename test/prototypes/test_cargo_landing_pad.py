# test_cargo_landing_pad.py

from draftsman.prototypes.cargo_landing_pad import (
    CargoLandingPad,
    cargo_landing_pads,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    pad = CargoLandingPad("cargo-landing-pad")

    with pytest.warns(UnknownEntityWarning):
        CargoLandingPad("unknown landing pad")


def test_flags():
    for pad_name in cargo_landing_pads:
        pad = CargoLandingPad(pad_name)
        assert pad.power_connectable == False
        assert pad.dual_power_connectable == False
        assert pad.circuit_connectable == True
        assert pad.dual_circuit_connectable == False