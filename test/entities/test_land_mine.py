# test_land_mine.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LandMine, land_mines
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LandMineTesting(unittest.TestCase):
    def test_contstructor_init(self):
        land_mine = LandMine()

        with pytest.warns(DraftsmanWarning):
            LandMine(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            LandMine("this is not a rocket silo")

    def test_mergable_with(self):
        landmine1 = LandMine("land-mine")
        landmine2 = LandMine("land-mine", tags={"some": "stuff"})

        assert landmine1.mergable_with(landmine1)

        assert landmine1.mergable_with(landmine2)
        assert landmine2.mergable_with(landmine1)

        landmine2.tile_position = (1, 1)
        assert not landmine1.mergable_with(landmine2)

    def test_merge(self):
        landmine1 = LandMine("land-mine")
        landmine2 = LandMine("land-mine", tags={"some": "stuff"})

        landmine1.merge(landmine2)
        del landmine2

        assert landmine1.tags == {"some": "stuff"}
