# test_land_mine.py

from draftsman.entity import LandMine, land_mines
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class LandMineTesting(TestCase):
    def test_contstructor_init(self):
        land_mine = LandMine()

        with self.assertWarns(DraftsmanWarning):
            LandMine(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityError):
            LandMine("this is not a rocket silo")