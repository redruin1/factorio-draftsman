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

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class BeaconTesting(TestCase):
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
        with self.assertRaises(InvalidItemError):
            beacon.set_item_request("incorrect", "nonsense")
        with self.assertRaises(TypeError):
            beacon.set_item_request("speed-module-2", "nonsense")
