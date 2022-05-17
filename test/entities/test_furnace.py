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

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class FurnaceTesting(unittest.TestCase):
    def test_constructor_init(self):
        furance = Furnace()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Furnace(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Furnace("not a heat pipe")

    def test_set_item_request(self):
        furnace = Furnace("stone-furnace")

        # Module on stone furnace
        with self.assertWarns(ModuleCapacityWarning):
            furnace.set_item_request("speed-module", 2)

        # Fuel on electric furnace
        # furnace.set_item_request("coal", 100)
        # self.assertEqual(furnace.items, {"productivity-module-3": 2, "coal": 100})

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
