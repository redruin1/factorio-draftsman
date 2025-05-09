# test_cargo_landing_pad.py

from draftsman.constants import LogisticModeOfOperation
from draftsman.prototypes.cargo_landing_pad import (
    CargoLandingPad,
    cargo_landing_pads,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    pad = CargoLandingPad(
        "cargo-landing-pad", mode_of_operation=LogisticModeOfOperation.SET_REQUESTS
    )
    assert pad.to_dict() == {
        "name": "cargo-landing-pad",
        "position": {"x": 4.0, "y": 4.0},
        "control_behavior": {
            "circuit_mode_of_operation": LogisticModeOfOperation.SET_REQUESTS,
        },
    }

    with pytest.warns(UnknownEntityWarning):
        CargoLandingPad("unknown landing pad")


def test_flags():
    for pad_name in cargo_landing_pads:
        pad = CargoLandingPad(pad_name)
        assert pad.power_connectable == False
        assert pad.dual_power_connectable == False
        assert pad.circuit_connectable == True
        assert pad.dual_circuit_connectable == False
