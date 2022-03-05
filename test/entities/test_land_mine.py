# test_land_mine.py

from draftsman.entity import LandMine, land_mines
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class LandMineTesting(TestCase):
    def test_default_constructor(self):
        land_mine = LandMine()
        self.assertEqual(
            land_mine.to_dict(),
            {
                "name": "land-mine",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_contstructor_init(self):
        land_mine = LandMine()

        with self.assertWarns(UserWarning):
            LandMine(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            LandMine("this is not a rocket silo")