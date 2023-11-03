# test_furnace.py

from draftsman.entity import Furnace, furnaces, Container
from draftsman.error import InvalidItemError
from draftsman.warning import (
    ModuleCapacityWarning,
    ModuleNotAllowedWarning,
    ItemLimitationWarning,
    ItemCapacityWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning
)

from collections.abc import Hashable
import pytest


class TestFurnace:
    def test_constructor_init(self):
        furnace = Furnace("stone-furnace")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Furnace("stone-furnace", unused_keyword="whatever")
        with pytest.warns(UnknownEntityWarning):
            Furnace("not a furnace")

        # Errors

    def test_set_item_request(self):
        furnace = Furnace("stone-furnace")

        print(furnace.allowed_modules)

        # Module on stone furnace disallowed
        with pytest.warns(ModuleNotAllowedWarning):
            furnace.set_item_request("speed-module", 2)
        assert furnace.items == {"speed-module": 2}

        # Too much fuel
        with pytest.warns(ItemCapacityWarning):
            furnace.set_item_request("coal", 100)
        assert furnace.items == {"speed-module": 2, "coal": 100}

        # Fuel, but not used
        with pytest.warns(ItemLimitationWarning):
            furnace.set_item_request("uranium-fuel-cell", 1)
        assert furnace.items == {"speed-module": 2, "coal": 100, "uranium-fuel-cell": 1}

        furnace = Furnace("electric-furnace")
        # Module on electric furnace
        furnace.set_item_request("productivity-module-3", 2)
        assert furnace.items == {"productivity-module-3": 2}
        assert furnace.module_slots_occupied == 2

        # Fuel on electric furnace
        with pytest.warns(ItemLimitationWarning):
            furnace.set_item_request("coal", 100)
        assert furnace.items == {"productivity-module-3": 2, "coal": 100}

        # Non smeltable item and not fuel
        furnace.items = {}
        with pytest.warns(ItemLimitationWarning):
            furnace.set_item_request("copper-plate", 100)
        assert furnace.items == {"copper-plate": 100}
        assert furnace.module_slots_occupied == 0

        furnace.items = {}
        assert furnace.items == {}
        assert furnace.module_slots_occupied == 0

        # Errors
        with pytest.raises(TypeError):
            furnace.set_item_request("incorrect", "nonsense")
        # with pytest.raises(InvalidItemError): # TODO
        #     furnace.set_item_request("incorrect", 100)
        with pytest.raises(TypeError):
            furnace.set_item_request("speed-module-2", TypeError)
        # with pytest.raises(ValueError): # TODO
        #     furnace.set_item_request("speed-module-2", -1)

        assert furnace.items == {}
        assert furnace.module_slots_occupied == 0

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
        furnace2 = Furnace(
            "stone-furnace", items={"copper-ore": 50}, tags={"some": "stuff"}
        )

        furnace1.merge(furnace2)
        del furnace2

        assert furnace1.items == {"copper-ore": 50}
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
