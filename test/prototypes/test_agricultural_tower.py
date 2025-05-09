# test_agricultural_tower.py

from draftsman.prototypes.agricultural_tower import (
    AgriculturalTower,
    agricultural_towers,
)
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    tower = AgriculturalTower("agricultural-tower")
    assert tower.to_dict() == {
        "name": "agricultural-tower",
        "position": {"x": 1.5, "y": 1.5},
    }

    with pytest.warns(UnknownEntityWarning):
        AgriculturalTower("unknown agricultural tower")


def test_flags():
    for tower_name in agricultural_towers:
        tower = AgriculturalTower(tower_name)
        assert tower.power_connectable == False
        assert tower.dual_power_connectable == False
        assert tower.circuit_connectable == True
        assert tower.dual_circuit_connectable == False
