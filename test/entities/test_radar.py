# test_radar.py

from draftsman.entity import Radar, radars
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class RadarTesting(TestCase):
    def test_contstructor_init(self):
        radar = Radar()

        with self.assertWarns(DraftsmanWarning):
            Radar(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityError):
            Radar("this is not a radar")