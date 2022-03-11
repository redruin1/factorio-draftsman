# test_beacon.py

from draftsman.entity import Beacon, beacons
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class BeaconTesting(TestCase):
    def test_contstructor_init(self):
        beacon = Beacon()

        with self.assertWarns(DraftsmanWarning):
            Beacon(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityError):
            Beacon("this is not a beacon")