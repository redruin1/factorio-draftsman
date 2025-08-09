# test_electric_turret.py

from draftsman.constants import Direction
from draftsman.prototypes.electric_turret import (
    ElectricTurret,
    electric_turrets,
)
from draftsman.signatures import Condition
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_electric_turret():
    return ElectricTurret(
        "laser-turret",
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
        priority_list=["medium-biter"],
        ignore_unprioritized=True,
        set_priority_list=True,
        set_ignore_unprioritized=True,
        ignore_unlisted_targets_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        read_ammo=False,
        # item_requests=[
        #     AttrsItemRequest(
        #         id="firearm-magazine",
        #         items=AttrsItemSpecification(
        #             in_inventory=[
        #                 AttrsInventoryLocation(
        #                     inventory=Inventory.turret_ammo, stack=0, count=200
        #                 )
        #             ]
        #         ),
        #     )
        # ],
        tags={"blah": "blah"},
    )


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
