# test_land_mine.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LandMine, land_mines
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class LandMineTesting(TestCase):
    def test_contstructor_init(self):
        land_mine = LandMine()

        with self.assertWarns(DraftsmanWarning):
            LandMine(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            LandMine("this is not a rocket silo")
