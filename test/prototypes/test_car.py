# test_car.py

from draftsman.constants import Orientation, ValidationMode
from draftsman.prototypes.car import (
    Car,
    cars,
)
from draftsman.signatures import (
    BlueprintInsertPlan,
    ItemInventoryPositions,
    EquipmentComponent,
)
import draftsman.validators
from draftsman.warning import UnknownEntityWarning

import pytest


@pytest.fixture
def valid_car():
    with draftsman.validators.set_mode(ValidationMode.MINIMUM):
        return Car(
            "tank",
            id="test",
            quality="uncommon",
            tile_position=(1, 1),
            orientation=Orientation.EAST,
            item_requests=[
                BlueprintInsertPlan(
                    id="energy-shield-equipment",
                    items=ItemInventoryPositions(grid_count=1),
                )
            ],
            equipment=[
                EquipmentComponent(equipment="energy-shield-equipment", position=(0, 0))
            ],
            enable_logistics_while_moving=False,
            driver_is_main_gunner=True,
            selected_gun_index=2,
        )


def test_constructor():
    car = Car("car")

    with pytest.warns(UnknownEntityWarning):
        Car("this is not a car")


def test_flags():
    for car_name in cars:
        car = Car(car_name)
        assert car.power_connectable == False
        assert car.dual_power_connectable == False
        assert car.circuit_connectable == False
        assert car.dual_circuit_connectable == False
