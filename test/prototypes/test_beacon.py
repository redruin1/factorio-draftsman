# test_beacon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Beacon, beacons, Container
from draftsman.error import InvalidEntityError, InvalidItemError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleLimitationWarning,
    ItemLimitationWarning,
)

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BeaconTesting(unittest.TestCase):
    def test_contstructor_init(self):
        beacon = Beacon()

        with pytest.warns(DraftsmanWarning):
            Beacon(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            Beacon("this is not a beacon")

    def test_set_item_request(self):
        beacon = Beacon()
        beacon.set_item_request("speed-module-3", 1)
        assert beacon.items == {"speed-module-3": 1}
        with pytest.warns(ModuleLimitationWarning):
            beacon.set_item_request("productivity-module-3", 1)

        beacon.set_item_requests(None)
        with pytest.warns(ItemLimitationWarning):
            beacon.set_item_request("steel-plate", 2)

        # Errors
        with pytest.raises(TypeError):
            beacon.set_item_request("incorrect", "nonsense")
        with pytest.raises(InvalidItemError):
            beacon.set_item_request("incorrect", 100)
        with pytest.raises(TypeError):
            beacon.set_item_request("speed-module-2", "nonsense")

    def test_mergable_with(self):
        beacon1 = Beacon("beacon")
        beacon2 = Beacon("beacon", items={"speed-module-2": 2})

        assert beacon1.mergable_with(beacon2)
        assert beacon2.mergable_with(beacon1)

        beacon2.tile_position = (1, 1)
        assert not beacon1.mergable_with(beacon2)

    def test_merge(self):
        beacon1 = Beacon("beacon")
        beacon2 = Beacon("beacon", items={"speed-module-2": 2})

        beacon1.merge(beacon2)
        del beacon2

        assert beacon1.items == {"speed-module-2": 2}

    def test_eq(self):
        beacon1 = Beacon("beacon")
        beacon2 = Beacon("beacon")

        assert beacon1 == beacon2

        beacon1.set_item_request("speed-module-3", 2)

        assert beacon1 != beacon2

        container = Container()

        assert beacon1 != container
        assert beacon2 != container

        # hashable
        assert isinstance(beacon1, Hashable)
