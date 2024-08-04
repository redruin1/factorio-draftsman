# test_fluid_wagon.py

from draftsman.entity import FluidWagon, fluid_wagons, Container
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestFluidWagon:
    def test_constructor_init(self):
        fluid_wagon = FluidWagon(
            "fluid-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
        )
        assert fluid_wagon.to_dict() == {
            "name": "fluid-wagon",
            "position": {"x": 1.0, "y": 1.0},
            "orientation": 0.75,
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            FluidWagon("fluid-wagon", unused_keyword="whatever").validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            FluidWagon("this is not a fluid wagon").validate().reissue_all()
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with pytest.raises(DataFormatError):
            FluidWagon("fluid-wagon", orientation="wrong").validate().reissue_all()

    def test_mergable_with(self):
        wagon1 = FluidWagon("fluid-wagon")
        wagon2 = FluidWagon("fluid-wagon", tags={"some": "stuff"})

        assert wagon1.mergable_with(wagon1)

        assert wagon1.mergable_with(wagon2)
        assert wagon2.mergable_with(wagon1)

        wagon2.orientation = 0.5
        assert not wagon1.mergable_with(wagon2)

    def test_merge(self):
        wagon1 = FluidWagon("fluid-wagon")
        wagon2 = FluidWagon("fluid-wagon", tags={"some": "stuff"})

        wagon1.merge(wagon2)
        del wagon2

        assert wagon1.tags == {"some": "stuff"}

    def test_eq(self):
        wagon1 = FluidWagon("fluid-wagon")
        wagon2 = FluidWagon("fluid-wagon")

        assert wagon1 == wagon2

        wagon1.tags = {"some": "stuff"}

        assert wagon1 != wagon2

        container = Container()

        assert wagon1 != container
        assert wagon2 != container

        # hashable
        assert isinstance(wagon1, Hashable)
