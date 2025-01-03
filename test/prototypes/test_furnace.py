# test_furnace.py

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

from collections.abc import Hashable
import pytest


class TestFurnace:
    def test_constructor_init(self):
        furnace = Furnace("stone-furnace")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Furnace("stone-furnace", unused_keyword="whatever").validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            Furnace("not a furnace").validate().reissue_all()

        # Errors

    # def test_set_item_request(self):
    #     furnace = Furnace("stone-furnace")
    #     assert furnace.allowed_modules == {
    #         "efficiency-module",
    #         "efficiency-module-2",
    #         "efficiency-module-3",
    #         "speed-module",
    #         "speed-module-2",
    #         "speed-module-3",
    #     }
    #     assert furnace.total_module_slots == 0

    #     # No slots on stone furnace for modules
    #     with pytest.warns(ModuleCapacityWarning):
    #         furnace.set_item_request("speed-module", 2)
    #     assert furnace.items == {"speed-module": 2}

    #     # Too much fuel
    #     with pytest.warns(FuelCapacityWarning):
    #         furnace.items = {"coal": 100}
    #     assert furnace.items == {"coal": 100}

    #     # Fuel, but not used
    #     with pytest.warns(FuelLimitationWarning):
    #         furnace.items = {"uranium-fuel-cell": 1}
    #     assert furnace.items == {"uranium-fuel-cell": 1}

    #     furnace = Furnace("electric-furnace")
    #     assert furnace.allowed_modules == {
    #         "speed-module",
    #         "speed-module-2",
    #         "speed-module-3",
    #         "efficiency-module",
    #         "efficiency-module-2",
    #         "efficiency-module-3",
    #         "productivity-module",
    #         "productivity-module-2",
    #         "productivity-module-3",
    #         "quality-module",
    #         "quality-module-2",
    #         "quality-module-3",
    #     }
    #     assert furnace.total_module_slots == 2
    #     # Module on electric furnace
    #     furnace.set_item_request("productivity-module-3", 2)
    #     assert furnace.items == {"productivity-module-3": 2}
    #     assert furnace.module_slots_occupied == 2

    #     with pytest.warns(ModuleCapacityWarning):
    #         furnace.set_item_request("speed-module", 2)
    #     assert furnace.items == {"productivity-module-3": 2, "speed-module": 2}
    #     assert furnace.module_slots_occupied == 4

    #     furnace.items = None

    #     # Fuel on electric furnace
    #     with pytest.warns(ItemLimitationWarning):
    #         furnace.set_item_request("coal", 100)
    #     assert furnace.items == {"coal": 100}

    #     # Too much of valid ingredient input
    #     with pytest.warns(ItemCapacityWarning):
    #         furnace.items = {"iron-ore": 100}  # 2 stacks instead of 1
    #     assert furnace.items == {"iron-ore": 100}

    #     # Non smeltable item and not fuel
    #     furnace.items = {}
    #     with pytest.warns(ItemLimitationWarning):
    #         furnace.set_item_request("copper-plate", 100)
    #     assert furnace.items == {"copper-plate": 100}
    #     assert furnace.module_slots_occupied == 0
    #     assert furnace.fuel_slots_occupied == 0

    #     furnace.items = {}
    #     assert furnace.items == {}
    #     assert furnace.module_slots_occupied == 0
    #     assert furnace.fuel_slots_occupied == 0

    #     # Errors
    #     with pytest.raises(DataFormatError):
    #         furnace.set_item_request("unknown", "incorrect")
    #     with pytest.warns(UnknownItemWarning):
    #         furnace.set_item_request("unknown", 100)
    #     with pytest.raises(DataFormatError):
    #         furnace.set_item_request("speed-module-2", TypeError)
    #     with pytest.raises(DataFormatError):
    #         furnace.set_item_request("speed-module-2", -1)

    #     assert furnace.items == {"unknown": 100}
    #     assert furnace.module_slots_occupied == 0
    #     assert furnace.fuel_slots_occupied == 0

    def test_mergable_with(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace(
            "stone-furnace", items={"copper-ore": 50}, tags={"some": "stuff"}
        )

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
