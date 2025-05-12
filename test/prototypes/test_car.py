# test_car.py

from draftsman.constants import Orientation
from draftsman.prototypes.car import (
    Car,
    cars,
)
from draftsman.signatures import AttrsItemRequest, AttrsItemSpecification, AttrsInventoryLocation, EquipmentComponent
from draftsman.warning import UnknownEntityWarning

import pytest

valid_car = Car(
    "tank",
    id="test",
    quality="uncommon",
    tile_position=(1, 1),
    orientation=Orientation.EAST,
    item_requests=[
        AttrsItemRequest(
            id="energy-shield-equipment",
            items=AttrsItemSpecification(
                grid_count=1
            ),
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


def test_json_schema():
    assert Car.json_schema(version=(1, 0)) is None
    assert Car.json_schema(version=(2, 0)) == {
        "$id": "urn:factorio:entity:car",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "entity_number": {"$ref": "urn:uint64"},
            "name": {"type": "string"},
            "position": {
                "$ref": "urn:factorio:position",
            },
            "quality": {"$ref": "urn:factorio:quality-name"},
            "orientation": {"type": "number"},
            "items": {
                "type": "array",
                "items": {"$ref": "urn:factorio:item-request"},
            },
            "enable_logistics_while_moving": {"type": "boolean", "default": "true"},
            "grid": {
                "type": "array",
                "items": {"$ref": "urn:factorio:equipment-component"},
            },
            "trunk_inventory": {"type": "null"},
            "ammo_inventory": {"type": "null"},
            "driver_is_main_gunner": {"type": "boolean", "default": "false"},
            "selected_gun_index": {"$ref": "urn:uint32", "default": 1},
            "tags": {"type": "object"},
        },
        "required": ["entity_number", "name", "position"],
    }

def test_flags():
    for car_name in cars:
        car = Car(car_name)
        assert car.power_connectable == False
        assert car.dual_power_connectable == False
        assert car.circuit_connectable == False
        assert car.dual_circuit_connectable == False
