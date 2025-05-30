# test_furnace.py

from draftsman.constants import Direction, Inventory
from draftsman.entity import Furnace, furnaces, Container
from draftsman.error import DataFormatError
from draftsman.warning import (
    ModuleCapacityWarning,
    ModuleNotAllowedWarning,
    ItemCapacityWarning,
    ItemLimitationWarning,
    FuelCapacityWarning,
    FuelLimitationWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)
from draftsman.signatures import (
    AttrsItemRequest,
    AttrsItemID,
    AttrsItemSpecification,
    AttrsInventoryLocation,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_furnace():
    if len(furnaces) == 0:
        return None
    return Furnace(
        "electric-furnace",
        id="test",
        quality="uncommon",
        direction=Direction.EAST,
        tile_position=(1, 1),
        item_requests=[
            AttrsItemRequest(
                id=AttrsItemID(name="speed-module-3"),
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.furnace_modules, stack=0, count=1
                        ),
                        AttrsInventoryLocation(
                            inventory=Inventory.furnace_modules, stack=1, count=1
                        ),
                    ]
                ),
            )
        ],
        tags={"blah": "blah"},
    )


class TestFurnace:
    def test_constructor_init(self):
        furnace = Furnace("stone-furnace")

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Furnace("not a furnace").validate().reissue_all()

        # Errors

    def test_allowed_effects(self):
        furnace = Furnace("stone-furnace")
        assert furnace.allowed_effects == {"consumption", "speed", "pollution"}
        furnace = Furnace("electric-furnace")
        assert furnace.allowed_effects == {
            "speed",
            "productivity",
            "quality",
            "pollution",
            "consumption",
        }

        with pytest.warns(UnknownEntityWarning):
            furnace = Furnace("unknown-furance")
        assert furnace.allowed_effects == None

    def test_allowed_input_ingredients(self):
        furnace = Furnace("stone-furnace")
        assert furnace.allowed_input_ingredients == {
            "iron-plate",
            "stone",
            "iron-ore",
            "lithium",
            "copper-ore",
        }
        furnace = Furnace("electric-furnace")
        assert furnace.allowed_input_ingredients == {
            "iron-plate",
            "stone",
            "iron-ore",
            "lithium",
            "copper-ore",
        }

        with pytest.warns(UnknownEntityWarning):
            furnace = Furnace("unknown-furance")
        assert furnace.allowed_input_ingredients == None

    def test_fuel_input_size(self):
        furnace = Furnace("stone-furnace")
        assert furnace.energy_source["type"] == "burner"
        assert furnace.fuel_input_size == 1
        assert furnace.fuel_output_size == 0

        furnace = Furnace("electric-furnace")
        assert furnace.energy_source["type"] == "electric"
        assert furnace.fuel_input_size == 0
        assert furnace.fuel_output_size == 0

        furnace = Furnace("unknown-furnace", validate_assignment="none")
        assert furnace.energy_source is None
        assert furnace.fuel_input_size is None
        assert furnace.fuel_output_size is None

    def test_set_item_request(self):
        furnace = Furnace("stone-furnace")
        assert furnace.allowed_modules == {
            "efficiency-module",
            "efficiency-module-2",
            "efficiency-module-3",
            "speed-module",
            "speed-module-2",
            "speed-module-3",
        }
        assert furnace.total_module_slots == 0

        # # No slots on stone furnace for modules
        # with pytest.warns(ModuleCapacityWarning):
        #     furnace.set_item_request("speed-module", 2)
        # assert furnace.items == {"speed-module": 2}

        # # Too much fuel
        # with pytest.warns(FuelCapacityWarning):
        #     furnace.items = {"coal": 100}
        # assert furnace.items == {"coal": 100}

        # # Fuel, but not used
        # with pytest.warns(FuelLimitationWarning):
        #     furnace.items = {"uranium-fuel-cell": 1}
        # assert furnace.items == {"uranium-fuel-cell": 1}

        furnace = Furnace("electric-furnace")

        # Test setting to None removes
        furnace.set_item_request("coal", 50, inventory=Inventory.fuel)
        furnace.set_item_request("coal", None)
        assert furnace.item_requests == []

        # Test resetting count of existing request
        furnace.set_item_request(
            "coal", 25, inventory=Inventory.fuel, quality="legendary"
        )
        furnace.set_item_request(
            "coal", 50, inventory=Inventory.fuel, quality="legendary"
        )
        assert furnace.item_requests == [
            AttrsItemRequest(
                id=AttrsItemID(name="coal", quality="legendary"),
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.fuel, stack=0, count=50
                        )
                    ]
                ),
            )
        ]

        # Test setting to None resets to empty list
        furnace.item_requests = None
        assert furnace.item_requests == []

    def test_request_modules(self):
        furnace = Furnace("electric-furnace")
        furnace.request_modules("productivity-module-3", (0, 1), "legendary")
        assert furnace.item_requests == [
            AttrsItemRequest(
                id=AttrsItemID(name="productivity-module-3", quality="legendary"),
                items=AttrsItemSpecification(
                    in_inventory=[
                        AttrsInventoryLocation(
                            inventory=Inventory.furnace_modules,
                            stack=0,
                        ),
                        AttrsInventoryLocation(
                            inventory=Inventory.furnace_modules,
                            stack=1,
                        ),
                    ]
                )
            )
        ]

    def test_mergable_with(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace("stone-furnace", tags={"some": "stuff"})

        assert furnace1.mergable_with(furnace1)

        assert furnace1.mergable_with(furnace2)
        assert furnace2.mergable_with(furnace1)

        furnace2.tile_position = (5, 5)
        assert not furnace1.mergable_with(furnace2)

        furnace2 = Furnace("electric-furnace")
        assert not furnace1.mergable_with(furnace2)

    def test_merge(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace("stone-furnace", tags={"some": "stuff"})

        furnace1.merge(furnace2)
        del furnace2

        assert furnace1.tags == {"some": "stuff"}

    def test_eq(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace("stone-furnace")

        assert furnace1 == furnace2

        furnace1.tags = {"some": "stuff"}

        assert furnace1 != furnace2

        container = Container()

        assert furnace1 != container
        assert furnace2 != container

        # hashable
        assert isinstance(furnace1, Hashable)
