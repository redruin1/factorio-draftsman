# test_radar.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Radar, radars
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class RadarTesting(unittest.TestCase):
    def test_contstructor_init(self):
        radar = Radar()

        with pytest.warns(DraftsmanWarning):
            Radar(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            Radar("this is not a radar")

    def test_mergable_with(self):
        radar1 = Radar("radar")
        radar2 = Radar("radar", tags={"some": "stuff"})

        assert radar1.mergable_with(radar1)

        assert radar1.mergable_with(radar2)
        assert radar2.mergable_with(radar1)

        radar2.tile_position = (1, 1)
        assert not radar1.mergable_with(radar2)

    def test_merge(self):
        radar1 = Radar("radar")
        radar2 = Radar("radar", tags={"some": "stuff"})

        radar1.merge(radar2)
        del radar2

        assert radar1.tags == {"some": "stuff"}
