# test_cargo_bay.py

from draftsman.prototypes.cargo_bay import (
    CargoBay,
    cargo_bays,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_cargo_bay():
    if len(cargo_bays) == 0:
        return None
    return CargoBay(
        "cargo-bay",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        tags={"blah": "blah"},
    )


def test_constructor():
    bay = CargoBay("cargo-bay")

    with pytest.warns(UnknownEntityWarning):
        CargoBay("unknown cargo bay")


def test_flags():
    for bay_name in cargo_bays:
        bay = CargoBay(bay_name)
        assert bay.power_connectable == False
        assert bay.dual_power_connectable == False
        assert bay.circuit_connectable == False
        assert bay.dual_circuit_connectable == False
