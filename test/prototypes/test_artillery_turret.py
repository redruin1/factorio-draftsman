# test_artillery_turret.py

from draftsman.constants import Direction, Inventory
from draftsman.prototypes.artillery_turret import (
    ArtilleryTurret,
    artillery_turrets,
)
from draftsman.signatures import (
    Condition,
    BlueprintInsertPlan,
    ItemInventoryPositions,
    InventoryPosition,
)
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_artillery_turret():
    if len(artillery_turrets) == 0:
        return None
    return ArtilleryTurret(
        "artillery-turret",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        circuit_enabled=True,
        circuit_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        connect_to_logistic_network=True,
        logistic_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        read_ammo=False,
        item_requests=[
            BlueprintInsertPlan(
                id="artillery-shell",
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=Inventory.artillery_turret_ammo, stack=0, count=1
                        )
                    ]
                ),
            )
        ],
        tags={"blah": "blah"},
    )


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
