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

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class FurnaceTesting(unittest.TestCase):
    def test_constructor_init(self):
        furnace = Furnace("stone-furnace")

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Furnace("stone-furnace", unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Furnace("not a furnace")

    def test_set_item_request(self):
        furnace = Furnace("stone-furnace")

        # Module on stone furnace
        with self.assertWarns(ModuleCapacityWarning):
            furnace.set_item_request("speed-module", 2)

        # TODO: Fuel on electric furnace
        # furnace.set_item_request("coal", 100)
        # self.assertEqual(furnace.items, {"speed-module": 2, "coal": 100})

        furnace = Furnace("electric-furnace")
        # Module on electric furnace
        furnace.set_item_request("productivity-module-3", 2)
        self.assertEqual(furnace.items, {"productivity-module-3": 2})
        self.assertEqual(furnace.module_slots_occupied, 2)

        # Fuel on electric furnace
        with self.assertWarns(ItemLimitationWarning):
            furnace.set_item_request("coal", 100)
        self.assertEqual(furnace.items, {"productivity-module-3": 2, "coal": 100})

        # Non smeltable item and not fuel
        furnace.set_item_requests(None)
        with self.assertWarns(ItemLimitationWarning):
            furnace.set_item_request("copper-plate", 100)
        self.assertEqual(furnace.items, {"copper-plate": 100})
        self.assertEqual(furnace.module_slots_occupied, 0)

        furnace.set_item_requests(None)
        self.assertEqual(furnace.items, {})
        self.assertEqual(furnace.module_slots_occupied, 0)

        # Errors
        with self.assertRaises(TypeError):
            furnace.set_item_request("incorrect", "nonsense")
        with self.assertRaises(InvalidItemError):
            furnace.set_item_request("incorrect", 100)
        with self.assertRaises(TypeError):
            furnace.set_item_request("speed-module-2", TypeError)
        with self.assertRaises(ValueError):
            furnace.set_item_request("speed-module-2", -1)

        self.assertEqual(furnace.items, {})
        self.assertEqual(furnace.module_slots_occupied, 0)

    def test_mergable_with(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace(
            "stone-furnace", items={"copper-ore": 100}, tags={"some": "stuff"}
        )

        self.assertTrue(furnace1.mergable_with(furnace1))

        self.assertTrue(furnace1.mergable_with(furnace2))
        self.assertTrue(furnace2.mergable_with(furnace1))

        furnace2.tile_position = (5, 5)
        self.assertFalse(furnace1.mergable_with(furnace2))

        furnace2 = Furnace("electric-furnace")
        self.assertFalse(furnace1.mergable_with(furnace2))

    def test_merge(self):
        furnace1 = Furnace("stone-furnace")
        furnace2 = Furnace(
            "stone-furnace", items={"copper-ore": 100}, tags={"some": "stuff"}
        )

        furnace1.merge(furnace2)
        del furnace2

        self.assertEqual(furnace1.items, {"copper-ore": 100})
        self.assertEqual(furnace1.tags, {"some": "stuff"})
