# test_fluid_turret.py

from draftsman.prototypes.fluid_turret import (
    FluidTurret,
    fluid_turrets,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    turret = FluidTurret("flamethrower-turret")

    with pytest.warns(UnknownEntityWarning):
        FluidTurret("not a fluid turret")


def test_flags():
    for turret_name in fluid_turrets:
        turret = FluidTurret(turret_name)
        assert turret.power_connectable == False
        assert turret.dual_power_connectable == False
        assert turret.circuit_connectable == True
        assert turret.dual_circuit_connectable == False