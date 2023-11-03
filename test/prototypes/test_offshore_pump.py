# test_offshore_pump.py

from draftsman.entity import OffshorePump, offshore_pumps, Container
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestOffshorePump:
    def test_constructor_init(self):
        pump = OffshorePump()

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            OffshorePump(unused_keyword="whatever")
        with pytest.warns(UnknownKeywordWarning):
            OffshorePump(control_behavior={"unused_key": "something"})
        with pytest.warns(UnknownEntityWarning):
            OffshorePump("not a heat pipe")

        # Errors
        with pytest.raises(DataFormatError):
            OffshorePump(control_behavior="incorrect")

    def test_mergable_with(self):
        pump1 = OffshorePump("offshore-pump")
        pump2 = OffshorePump("offshore-pump", tags={"some": "stuff"})

        assert pump1.mergable_with(pump1)

        assert pump1.mergable_with(pump2)
        assert pump2.mergable_with(pump1)

        pump2.tile_position = (1, 1)
        assert not pump1.mergable_with(pump2)

    def test_merge(self):
        pump1 = OffshorePump("offshore-pump")
        pump2 = OffshorePump("offshore-pump", tags={"some": "stuff"})

        pump1.merge(pump2)
        del pump2

        assert pump1.tags == {"some": "stuff"}

    def test_eq(self):
        pump1 = OffshorePump("offshore-pump")
        pump2 = OffshorePump("offshore-pump")

        assert pump1 == pump2

        pump1.tags = {"some": "stuff"}

        assert pump1 != pump2

        container = Container()

        assert pump1 != container
        assert pump2 != container

        # hashable
        assert isinstance(pump1, Hashable)
