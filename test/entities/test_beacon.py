# test_beacon.py

from draftsman.entity import Beacon, beacons
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class BeaconTesting(TestCase):
    def test_default_constructor(self):
        beacon = Beacon()
        self.assertEqual(
            beacon.to_dict(),
            {
                "name": "beacon",
                "position": {"x": 1.5, "y": 1.5}
            }
        )

    def test_contstructor_init(self):
        beacon = Beacon()

        with self.assertWarns(UserWarning):
            Beacon(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            Beacon("this is not a beacon")