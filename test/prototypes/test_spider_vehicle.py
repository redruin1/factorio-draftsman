# test_spider_vehicle.py

from draftsman.error import DataFormatError
from draftsman.prototypes.spider_vehicle import SpiderVehicle, spider_vehicles
from draftsman.signatures import (
    AttrsColor,
    EquipmentComponent,
    EquipmentID,
    AttrsItemRequest,
    AttrsItemID,
    AttrsItemSpecification,
    ManualSection,
    SignalFilter,
)
from draftsman.warning import UnknownEntityWarning

import pytest
import copy


@pytest.fixture
def valid_spider_vehicle():
    if len(spider_vehicles) == 0:
        return None
    return SpiderVehicle(
        "spidertron",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        item_requests=[
            AttrsItemRequest(
                id="energy-shield-equipment",
                items=AttrsItemSpecification(grid_count=1),
            )
        ],
        equipment=[
            EquipmentComponent(equipment="energy-shield-equipment", position=(0, 0))
        ],
        trash_not_requested=True,
        request_from_buffers=False,
        requests_enabled=False,
        sections=[
            ManualSection(
                index=1, filters=[SignalFilter(index=1, name="iron-plate", count=50)]
            )
        ],
        enable_logistics_while_moving=False,
        driver_is_main_gunner=True,
        selected_gun_index=2,
        color=(0.5, 0.5, 0.5),
        auto_target_without_gunner=False,
        auto_target_with_gunner=True,
        tags={"blah": "blah"},
    )


def test_constructor():
    vehicle = SpiderVehicle(
        "spidertron",
        auto_target_without_gunner=False,
        auto_target_with_gunner=True,
    )
    assert vehicle.to_dict() == {
        "name": "spidertron",
        "position": {"x": 1.0, "y": 1.0},
        "automatic_targeting_parameters": {
            "auto_target_without_gunner": False,
            "auto_target_with_gunner": True,
        },
    }

    assert vehicle.to_dict(exclude_none=False) == {
        "name": "spidertron",
        "position": {"x": 1.0, "y": 1.0},
        "automatic_targeting_parameters": {
            "auto_target_without_gunner": False,
            "auto_target_with_gunner": True,
        },
    }

    assert vehicle.to_dict(exclude_defaults=False) == {
        "name": "spidertron",
        "position": {"x": 1.0, "y": 1.0},
        "quality": "normal",
        "automatic_targeting_parameters": {
            "auto_target_without_gunner": False,
            "auto_target_with_gunner": True,
        },
        "color": {"r": 255 / 255, "g": 127 / 255, "b": 0.0, "a": 127 / 255},
        "driver_is_main_gunner": False,
        "selected_gun_index": 1,
        "enable_logistics_while_moving": True,
        "grid": [],
        "items": [],
        "mirror": False,
        "request_filters": {
            "enabled": True,
            "request_from_buffers": True,
            "sections": [],
            "trash_not_requested": False,
        },
        "tags": {},
    }

    with pytest.warns(UnknownEntityWarning):
        SpiderVehicle("unknown vehicle")


def test_flags():
    for vehicle_name in spider_vehicles:
        vehicle = SpiderVehicle(vehicle_name)
        assert vehicle.power_connectable == False
        assert vehicle.dual_power_connectable == False
        assert vehicle.circuit_connectable == False
        assert vehicle.dual_circuit_connectable == False


def test_equipment_grid():
    """
    Test the read-only equipment grid attribute matches the expected values and
    parameters (as well as correctly adjusting to quality level).
    """
    spidertron = SpiderVehicle("spidertron")
    assert spidertron.equipment_grid is not None
    assert spidertron.equipment_grid.id == "spidertron-equipment-grid"
    assert spidertron.equipment_grid.equipment_categories == ["armor"]
    assert spidertron.equipment_grid.width == 10
    assert spidertron.equipment_grid.height == 6
    assert spidertron.equipment_grid.locked is False

    # Test equipment grid quality
    spidertron.quality = "legendary"
    assert spidertron.equipment_grid is not None
    assert spidertron.equipment_grid.id == "spidertron-equipment-grid"
    assert spidertron.equipment_grid.equipment_categories == ["armor"]
    assert spidertron.equipment_grid.width == 15
    assert spidertron.equipment_grid.height == 11
    assert spidertron.equipment_grid.locked is False

def test_equipment():
    """
    Using the equipment grid helper functions should bookkeep `equipment` as
    well as `item_requests`.
    """
    spidertron = SpiderVehicle("spidertron")

    with pytest.raises(DataFormatError):
        spidertron.equipment = "incorrect"

    spidertron.add_equipment("energy-shield-equipment", (0, 0))
    spidertron.add_equipment("battery-equipment", (2, 0), quality="legendary")
    spidertron.add_equipment("energy-shield-equipment", (3, 0))
    assert spidertron.equipment == [
        EquipmentComponent(
            equipment=EquipmentID(name="energy-shield-equipment"), position=(0, 0)
        ),
        EquipmentComponent(
            equipment=EquipmentID(name="battery-equipment", quality="legendary"),
            position=(2, 0),
        ),
        EquipmentComponent(
            equipment=EquipmentID(
                name="energy-shield-equipment",
            ),
            position=(3, 0),
        ),
    ]
    assert spidertron.item_requests == [
        AttrsItemRequest(
            id=AttrsItemID(name="energy-shield-equipment"),
            items=AttrsItemSpecification(grid_count=2),
        ),
        AttrsItemRequest(
            id=AttrsItemID(name="battery-equipment", quality="legendary"),
            items=AttrsItemSpecification(grid_count=1),
        ),
    ]
    assert spidertron.to_dict() == {
        "name": "spidertron",
        "position": {"x": 1.0, "y": 1.0},
        "grid": [
            {
                "equipment": {
                    "name": "energy-shield-equipment",
                },
                "position": {"x": 0, "y": 0},
            },
            {
                "equipment": {
                    "name": "battery-equipment",
                    "quality": "legendary",
                },
                "position": {"x": 2, "y": 0},
            },
            {
                "equipment": {
                    "name": "energy-shield-equipment",
                },
                "position": {"x": 3, "y": 0},
            },
        ],
        "items": [
            {
                "id": {
                    "name": "energy-shield-equipment",
                },
                "items": {"grid_count": 2},
            },
            {
                "id": {
                    "name": "battery-equipment",
                    "quality": "legendary",
                },
                "items": {"grid_count": 1},
            },
        ],
    }

    # Test remove all
    spider_copy = copy.deepcopy(spidertron)
    spider_copy.remove_equipment()
    assert spider_copy.equipment == []
    assert spider_copy.item_requests == []

    # Test remove specific
    spider_copy = copy.deepcopy(spidertron)
    spider_copy.remove_equipment(quality="normal")
    assert spider_copy.equipment == [
        EquipmentComponent(
            equipment={
                "name": "battery-equipment",
                "quality": "legendary",
            },
            position=(2, 0),
        ),
    ]
    assert spider_copy.item_requests == [
        AttrsItemRequest(
            id=AttrsItemID(name="battery-equipment", quality="legendary"),
            items=AttrsItemSpecification(grid_count=1),
        ),
    ]

    # Test full dict conversion
    spider_copy.equipment = [
        {
            "equipment": {
                "name": "battery-equipment",
                "quality": "legendary",
            },
            "position": {"x": 2, "y": 0},
        }
    ]
    assert spider_copy.equipment == [
        EquipmentComponent(
            equipment=EquipmentID(name="battery-equipment", quality="legendary"),
            position=(2, 0),
        ),
    ]


def test_color():
    vehicle = SpiderVehicle("spidertron")
    assert vehicle.color == AttrsColor(r=255 / 255, g=127 / 255, b=0.0, a=127 / 255)
    assert vehicle.to_dict() == {
        "name": "spidertron",
        "position": {"x": 1.0, "y": 1.0},
    }

    vehicle.color = (255, 0, 0)
    assert vehicle.color == AttrsColor(255, 0, 0)
    assert vehicle.to_dict() == {
        "name": "spidertron",
        "position": {"x": 1.0, "y": 1.0},
        "color": {
            "r": 255,
            "g": 0,
            "b": 0,
        },
    }
