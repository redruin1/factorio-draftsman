# test_radar.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Radar, radars
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class RadarTesting(unittest.TestCase):
    def test_contstructor_init(self):
        radar = Radar()

        with self.assertWarns(DraftsmanWarning):
            Radar(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Radar("this is not a radar")

    def test_mergable_with(self):
        radar1 = Radar("radar")
        radar2 = Radar("radar", tags={"some": "stuff"})

        self.assertTrue(radar1.mergable_with(radar1))

        self.assertTrue(radar1.mergable_with(radar2))
        self.assertTrue(radar2.mergable_with(radar1))

        radar2.tile_position = (1, 1)
        self.assertFalse(radar1.mergable_with(radar2))

    def test_merge(self):
        radar1 = Radar("radar")
        radar2 = Radar("radar", tags={"some": "stuff"})

        radar1.merge(radar2)
        del radar2

        self.assertEqual(radar1.tags, {"some": "stuff"})
