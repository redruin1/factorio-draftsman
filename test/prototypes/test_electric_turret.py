# test_electric_turret.py

from draftsman.prototypes.electric_turret import (
    ElectricTurret,
    electric_turrets,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    turret = ElectricTurret("laser-turret")

    with pytest.warns(UnknownEntityWarning):
        ElectricTurret("unknown electric turret")


def test_flags():
    for turret_name in electric_turrets:
        turret = ElectricTurret(turret_name)
        assert turret.power_connectable == False
        assert turret.dual_power_connectable == False
        assert turret.circuit_connectable == True
        assert turret.dual_circuit_connectable == False
