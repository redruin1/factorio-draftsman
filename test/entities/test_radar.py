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
