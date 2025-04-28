# test_boiler.py

from draftsman.entity import Boiler, boilers, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestBoiler:
    def test_constructor_init(self):
        boiler = Boiler("boiler")

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Boiler("not a boiler").validate().reissue_all()

        # Errors

    def test_mergable_with(self):
        boiler1 = Boiler("boiler")
        boiler2 = Boiler("boiler", tags={"some": "stuff"})

        assert boiler1.mergable_with(boiler2)
        assert boiler2.mergable_with(boiler1)

        boiler2.tile_position = [-10, -10]
        assert not boiler1.mergable_with(boiler2)

    def test_merge(self):
        boiler1 = Boiler("boiler")
        boiler2 = Boiler("boiler", tags={"some": "stuff"})

        boiler1.merge(boiler2)
        del boiler2

        assert boiler1.tags == {"some": "stuff"}

    def test_eq(self):
        boiler1 = Boiler("boiler")
        boiler2 = Boiler("boiler")

        assert boiler1 == boiler2

        boiler1.set_item_request("coal", 10)

        assert boiler1 != boiler2

        container = Container()

        assert boiler1 != container
        assert boiler2 != container

        # hashable
        assert isinstance(boiler1, Hashable)
