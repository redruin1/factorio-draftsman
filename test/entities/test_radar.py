# test_radar.py

from draftsman.entity import Radar, radars
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class RadarTesting(TestCase):
    def test_default_constructor(self):
        radar = Radar()
        self.assertEqual(
            radar.to_dict(),
            {
                "name": "radar",
                "position": {"x": 1.5, "y": 1.5}
            }
        )

    def test_contstructor_init(self):
        radar = Radar()

        with self.assertWarns(UserWarning):
            Radar(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            Radar("this is not a radar")