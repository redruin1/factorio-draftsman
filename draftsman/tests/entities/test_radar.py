# test_radar.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Radar, radars
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class RadarTesting(TestCase):
    def test_contstructor_init(self):
        radar = Radar()

        with self.assertWarns(DraftsmanWarning):
            Radar(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Radar("this is not a radar")
