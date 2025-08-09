# test_agricultural_tower.py

from draftsman.prototypes.agricultural_tower import (
    AgriculturalTower,
    agricultural_towers,
)
from draftsman.signatures import Condition
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_agricultural_tower():
    if len(agricultural_towers) == 0:
        return None
    return AgriculturalTower(
        "agricultural-tower",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        circuit_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        connect_to_logistic_network=True,
        logistic_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        read_contents=True,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(
    len(agricultural_towers) == 0, reason="No AgriculturalTowers to test"
)
class TestAgriculturalTower:
    def test_constructor(self):
        tower = AgriculturalTower("agricultural-tower")
        assert tower.to_dict() == {
            "name": "agricultural-tower",
            "position": {"x": 1.5, "y": 1.5},
        }

        with pytest.warns(UnknownEntityWarning):
            AgriculturalTower("unknown agricultural tower")

    def test_flags(self):
        for tower_name in agricultural_towers:
            tower = AgriculturalTower(tower_name)
            assert tower.power_connectable == False
            assert tower.dual_power_connectable == False
            assert tower.circuit_connectable == True
            assert tower.dual_circuit_connectable == False
