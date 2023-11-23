# test_land_mine.py

from draftsman.entity import LandMine, land_mines, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestLandMine:
    def test_contstructor_init(self):
        land_mine = LandMine()

        with pytest.warns(UnknownKeywordWarning):
            LandMine(unused_keyword="whatever")
        with pytest.warns(UnknownEntityWarning):
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

    def test_eq(self):
        landmine1 = LandMine("land-mine")
        landmine2 = LandMine("land-mine")

        assert landmine1 == landmine2

        landmine1.tags = {"some": "stuff"}

        assert landmine1 != landmine2

        container = Container()

        assert landmine1 != container
        assert landmine2 != container

        # hashable
        assert isinstance(landmine1, Hashable)
