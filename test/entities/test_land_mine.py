# test_land_mine.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LandMine, land_mines
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LandMineTesting(unittest.TestCase):
    def test_contstructor_init(self):
        land_mine = LandMine()

        with self.assertWarns(DraftsmanWarning):
            LandMine(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            LandMine("this is not a rocket silo")

    def test_mergable_with(self):
        landmine1 = LandMine("land-mine")
        landmine2 = LandMine("land-mine", tags={"some": "stuff"})

        self.assertTrue(landmine1.mergable_with(landmine1))

        self.assertTrue(landmine1.mergable_with(landmine2))
        self.assertTrue(landmine2.mergable_with(landmine1))

        landmine2.tile_position = (1, 1)
        self.assertFalse(landmine1.mergable_with(landmine2))

    def test_merge(self):
        landmine1 = LandMine("land-mine")
        landmine2 = LandMine("land-mine", tags={"some": "stuff"})

        landmine1.merge(landmine2)
        del landmine2

        self.assertEqual(landmine1.tags, {"some": "stuff"})
