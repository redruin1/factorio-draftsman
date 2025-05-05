# test_artillery_turret.py

from draftsman.prototypes.artillery_turret import (
    ArtilleryTurret,
    artillery_turrets,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    turret = ArtilleryTurret("artillery-turret")

    with pytest.warns(UnknownEntityWarning):
        ArtilleryTurret("unknown artillery turret")


def test_flags():
    for turret_name in artillery_turrets:
        turret = ArtilleryTurret(turret_name)
        assert turret.power_connectable == False
        assert turret.dual_power_connectable == False
        assert turret.circuit_connectable == True
        assert turret.dual_circuit_connectable == False