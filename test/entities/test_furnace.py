# test_furnace.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Furnace, furnaces
from draftsman.error import InvalidEntityError, InvalidItemError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleCapacityWarning,
    ItemLimitationWarning,
)

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class FurnaceTesting(unittest.TestCase):
    def test_constructor_init(self):
        furnace = Furnace("stone-furnace")

        # Warnings
        with pytest.warns(DraftsmanWarning):
            Furnace("stone-furnace", unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            Furnace("not a furnace")

    def test_set_item_request(self):
        furnace = Furnace("stone-furnace")

        # Module on stone furnace
        with pytest.warns(ModuleCapacityWarning):
            furnace.set_item_request("speed-module", 2)

        # TODO: Fuel on electric furnace
        # furnace.set_item_request("coal", 100)
        # self.assertEqual(furnace.items, {"speed-module": 2, "coal": 100})

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
        furnace.set_item_requests(None)
        with pytest.warns(ItemLimitationWarning):
            furnace.set_item_request("copper-plate", 100)
        assert furnace.items == {"copper-plate": 100}
        assert furnace.module_slots_occupied == 0

        furnace.set_item_requests(None)
        assert furnace.items == {}
        assert furnace.module_slots_occupied == 0

        # Errors
        with pytest.raises(TypeError):
            furnace.set_item_request("incorrect", "nonsense")
        with pytest.raises(InvalidItemError):
            furnace.set_item_request("incorrect", 100)
        with pytest.raises(TypeError):
            furnace.set_item_request("speed-module-2", TypeError)
        with pytest.raises(ValueError):
            furnace.set_item_request("speed-module-2", -1)

        assert furnace.items == {}
        assert furnace.module_slots_occupied == 0

    def test_mergable_with(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace(
            "stone-furnace", items={"copper-ore": 100}, tags={"some": "stuff"}
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
            "stone-furnace", items={"copper-ore": 100}, tags={"some": "stuff"}
        )

        furnace1.merge(furnace2)
        del furnace2

        assert furnace1.items == {"copper-ore": 100}
        assert furnace1.tags == {"some": "stuff"}
