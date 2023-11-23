# test_artillery_wagon.py

from draftsman.entity import ArtilleryWagon, artillery_wagons, Container
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import sys
import pytest


class TestArtilleryWagon:
    def test_constructor_init(self):
        artillery_wagon = ArtilleryWagon(
            "artillery-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
        )
        assert artillery_wagon.to_dict() == {
            "name": "artillery-wagon",
            "position": {"x": 1.0, "y": 1.0},
            "orientation": 0.75,
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            ArtilleryWagon("artillery-wagon", unused_keyword="whatever")
        with pytest.warns(UnknownEntityWarning):
            ArtilleryWagon("this is not an artillery wagon")

        # Errors
        with pytest.raises(DataFormatError):
            ArtilleryWagon("artillery-wagon", orientation="wrong")

    def test_mergable_with(self):
        wagon1 = ArtilleryWagon("artillery-wagon")
        wagon2 = ArtilleryWagon("artillery-wagon")

        assert wagon1.mergable_with(wagon2)
        assert wagon2.mergable_with(wagon1)

        wagon1.orientation = 0.5
        assert not wagon1.mergable_with(wagon2)

    def test_merge(self):
        wagon1 = ArtilleryWagon("artillery-wagon")
        wagon2 = ArtilleryWagon("artillery-wagon")
        wagon2.tags = {"some": "stuff"}

        wagon1.merge(wagon2)
        assert wagon1.tags == {"some": "stuff"}
        # Ensure wagon1's data remains valid even if wagon2 gets destroyed
        del wagon2
        assert wagon1.tags == {"some": "stuff"}

    def test_eq(self):
        wagon1 = ArtilleryWagon("artillery-wagon")
        wagon2 = ArtilleryWagon("artillery-wagon")

        assert wagon1 == wagon2

        wagon1.set_item_request("artillery-shell", 10)

        assert wagon1 != wagon2

        container = Container()

        assert wagon1 != container
        assert wagon2 != container

        # hashable
        assert isinstance(wagon1, Hashable)
