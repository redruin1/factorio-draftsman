# test_beacon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Beacon, beacons
from draftsman.error import InvalidEntityError, InvalidItemError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleLimitationWarning,
    ItemLimitationWarning,
)

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BeaconTesting(unittest.TestCase):
    def test_contstructor_init(self):
        beacon = Beacon()

        with self.assertWarns(DraftsmanWarning):
            Beacon(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Beacon("this is not a beacon")

    def test_set_item_request(self):
        beacon = Beacon()
        beacon.set_item_request("speed-module-3", 1)
        self.assertEqual(beacon.items, {"speed-module-3": 1})
        with self.assertWarns(ModuleLimitationWarning):
            beacon.set_item_request("productivity-module-3", 1)

        beacon.set_item_requests(None)
        with self.assertWarns(ItemLimitationWarning):
            beacon.set_item_request("steel-plate", 2)

        # Errors
        with self.assertRaises(TypeError):
            beacon.set_item_request("incorrect", "nonsense")
        with self.assertRaises(InvalidItemError):
            beacon.set_item_request("incorrect", 100)
        with self.assertRaises(TypeError):
            beacon.set_item_request("speed-module-2", "nonsense")

    def test_mergable_with(self):
        beacon1 = Beacon("beacon")
        beacon2 = Beacon("beacon", items={"speed-module-2": 2})

        self.assertTrue(beacon1.mergable_with(beacon2))
        self.assertTrue(beacon2.mergable_with(beacon1))

        beacon2.tile_position = (1, 1)
        self.assertFalse(beacon1.mergable_with(beacon2))

    def test_merge(self):
        beacon1 = Beacon("beacon")
        beacon2 = Beacon("beacon", items={"speed-module-2": 2})

        beacon1.merge(beacon2)
        del beacon2

        self.assertEqual(beacon1.items, {"speed-module-2": 2})
